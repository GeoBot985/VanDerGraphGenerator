"""Coordinate LLM mapping with deterministic fallback planning."""

from __future__ import annotations

from dataclasses import dataclass, field

from semantic_visual_builder.data.data_profiler import DatasetProfile
from semantic_visual_builder.knowledge.product_kb import ProductKnowledgeBase
from semantic_visual_builder.llm.llm_mapping_result import LlmMappingResult
from semantic_visual_builder.llm.llm_semantic_mapper import LlmSemanticMapper
from semantic_visual_builder.planning.clarification import ClarificationRequest
from semantic_visual_builder.planning.deterministic_fallback_mapper import (
    DeterministicFallbackMapper,
)
from semantic_visual_builder.planning.field_mapper import FieldMapper
from semantic_visual_builder.planning.visual_plan import get_role
from semantic_visual_builder.planning.visual_plan import (
    summarize_visual_plan,
    visual_plan_from_llm_draft,
)
from semantic_visual_builder.planning.visual_plan_schema import VisualPlan
from semantic_visual_builder.state.app_state import AppState
from semantic_visual_builder.validation.capability_validator import CapabilityValidator
from semantic_visual_builder.validation.validation_result import ValidationResult
from semantic_visual_builder.validation.visual_plan_validator import VisualPlanValidator


@dataclass
class PlanningResult:
    visual_plan: VisualPlan | None
    validation_result: ValidationResult
    mapping_method: str
    llm_mapping_result: LlmMappingResult | None = None
    used_fallback: bool = False
    messages: list[str] = field(default_factory=list)
    clarification_requests: list[ClarificationRequest] = field(default_factory=list)


class PlanningOrchestrator:
    """Choose between LLM and deterministic planning paths."""

    def __init__(
        self,
        llm_mapper: LlmSemanticMapper,
        deterministic_mapper: DeterministicFallbackMapper,
        field_mapper: FieldMapper,
        visual_plan_validator: VisualPlanValidator,
        capability_validator: CapabilityValidator,
    ):
        self.llm_mapper = llm_mapper
        self.deterministic_mapper = deterministic_mapper
        self.field_mapper = field_mapper
        self.visual_plan_validator = visual_plan_validator
        self.capability_validator = capability_validator

    def create_or_update_plan(
        self,
        user_message: str,
        app_state: AppState,
        use_llm: bool = True,
    ) -> PlanningResult:
        dataset_profile = app_state.dataset_context.profile
        product_kb = app_state.product_kb
        graph_matrix = app_state.graph_matrix
        current_plan_summary = (
            summarize_visual_plan(app_state.current_visual_plan)
            if app_state.current_visual_plan
            else None
        )

        selected_model = app_state.model_registry.selected_model
        llm_result: LlmMappingResult | None = None
        messages: list[str] = []
        attempted_llm = bool(
            use_llm and app_state.llm_mapping_enabled and selected_model
        )

        if attempted_llm:
            llm_result = self.llm_mapper.map_to_draft(
                model=selected_model,
                user_message=user_message,
                dataset_profile=dataset_profile,
                product_kb=product_kb,
                graph_matrix=graph_matrix,
                current_plan_summary=current_plan_summary,
            )
            if llm_result.draft is not None:
                plan = visual_plan_from_llm_draft(llm_result.draft)
                if dataset_profile is not None and self._needs_field_completion(plan):
                    completed_plan = self.field_mapper.complete_missing_roles(
                        user_message, dataset_profile, plan
                    )
                    if completed_plan != plan:
                        plan = completed_plan
                        messages.append(
                            "Completed missing LLM role fields with deterministic "
                            "field mapping."
                        )
                plan.metadata.mapping_method = (
                    "llm_with_repair" if llm_result.used_repair else "llm"
                )
                validation = self._validate(
                    plan, dataset_profile, product_kb, graph_matrix
                )
                if validation.is_valid:
                    return PlanningResult(
                        visual_plan=plan,
                        validation_result=validation,
                        mapping_method="llm_with_repair"
                        if llm_result.used_repair
                        else "llm",
                        llm_mapping_result=llm_result,
                        used_fallback=False,
                        messages=messages,
                        clarification_requests=[],
                    )
                unsupported_visual = any(
                    message.message.startswith("Unsupported chart_type")
                    or message.message.startswith("Unsupported diagram_type")
                    for message in validation.messages
                )
                if unsupported_visual:
                    messages.extend(message.message for message in validation.messages)
                    messages.append(
                        "The suggested visual type is not supported by the graph "
                        "matrix contract."
                    )
                    return PlanningResult(
                        visual_plan=None,
                        validation_result=validation,
                        mapping_method="llm_rejected",
                        llm_mapping_result=llm_result,
                        used_fallback=False,
                        messages=messages,
                        clarification_requests=[],
                    )
                messages.extend(message.message for message in validation.messages)
                messages.append(
                    "The LLM response did not pass the graph matrix contract."
                )
                messages.append("I used the limited deterministic fallback instead.")
            else:
                messages.extend(llm_result.errors or ["LLM mapping failed."])
                messages.append("I used the limited deterministic fallback instead.")
        else:
            if use_llm and not app_state.llm_mapping_enabled:
                messages.append(
                    "I could not use LLM semantic mapping because it is "
                    "disabled. I used the limited deterministic fallback instead."
                )
            elif use_llm and not selected_model:
                messages.append(
                    "I could not use LLM semantic mapping because no model is "
                    "selected. I used the limited deterministic fallback instead."
                )
            llm_result = None

        deterministic_plan = self.deterministic_mapper.map_request_to_plan(
            user_message, dataset_profile, graph_matrix
        )
        if dataset_profile is not None:
            deterministic_plan = self.field_mapper.propose_roles(
                user_message, dataset_profile, deterministic_plan
            )
        deterministic_plan.metadata.mapping_method = "deterministic_fallback"
        validation = self._validate(
            deterministic_plan, dataset_profile, product_kb, graph_matrix
        )
        return PlanningResult(
            visual_plan=deterministic_plan,
            validation_result=validation,
            mapping_method="deterministic_fallback",
            llm_mapping_result=llm_result,
            used_fallback=True,
            messages=messages,
            clarification_requests=[],
        )

    def _validate(
        self,
        plan,
        dataset_profile: DatasetProfile | None,
        product_kb: ProductKnowledgeBase | None,
        graph_matrix,
    ) -> ValidationResult:
        validation = self.visual_plan_validator.validate(
            plan, dataset_profile, graph_matrix
        )
        if product_kb is not None:
            capability_result = self.capability_validator.validate_against_capabilities(
                plan, product_kb
            )
            validation.messages.extend(capability_result.messages)
        return validation

    def _needs_field_completion(self, plan: VisualPlan) -> bool:
        return not plan.data_roles or any(role.field is None for role in plan.data_roles) or (
            plan.visual_kind == "chart"
            and plan.chart_type is not None
            and any(
                get_role(plan, required_role) is None
                or get_role(plan, required_role).field is None
                for required_role in {
                    "category",
                    "measure",
                    "x",
                    "y",
                    "time_or_order",
                    "value",
                    "x_category",
                    "y_category",
                    "series",
                    "stack",
                }
                if get_role(plan, required_role) is not None
            )
        )
