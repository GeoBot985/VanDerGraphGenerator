"""Coordinate LLM mapping with deterministic fallback planning."""

from __future__ import annotations

from dataclasses import dataclass, field

from semantic_visual_builder.data.data_profiler import DatasetProfile
from semantic_visual_builder.knowledge.product_kb import ProductKnowledgeBase
from semantic_visual_builder.llm.llm_mapping_result import LlmMappingResult
from semantic_visual_builder.llm.llm_semantic_mapper import LlmSemanticMapper
from semantic_visual_builder.planning.field_mapper import FieldMapper
from semantic_visual_builder.planning.intent_mapper import IntentMapper
from semantic_visual_builder.planning.visual_plan import summarize_visual_plan, visual_plan_from_llm_draft
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


class PlanningOrchestrator:
    """Choose between LLM and deterministic planning paths."""

    def __init__(
        self,
        llm_mapper: LlmSemanticMapper,
        deterministic_mapper: IntentMapper,
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
        current_plan_summary = summarize_visual_plan(app_state.current_visual_plan) if app_state.current_visual_plan else None

        selected_model = app_state.model_registry.selected_model
        llm_result: LlmMappingResult | None = None
        messages: list[str] = []
        attempted_llm = bool(use_llm and app_state.llm_mapping_enabled and selected_model)

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
                plan.metadata.mapping_method = "llm_with_repair" if llm_result.used_repair else "llm"
                validation = self._validate(plan, dataset_profile, product_kb)
                if validation.is_valid:
                    return PlanningResult(
                        visual_plan=plan,
                        validation_result=validation,
                        mapping_method="llm_with_repair" if llm_result.used_repair else "llm",
                        llm_mapping_result=llm_result,
                        used_fallback=False,
                        messages=messages,
                    )
                messages.extend(message.message for message in validation.messages)
                messages.append("LLM JSON draft was valid but plan validation failed.")
                messages.append("LLM mapping failed. Falling back to deterministic rule-based mapping.")
            else:
                messages.extend(llm_result.errors or ["LLM mapping failed."])
                messages.append("LLM mapping failed. Falling back to deterministic rule-based mapping.")
        else:
            if use_llm and not app_state.llm_mapping_enabled:
                messages.append("LLM semantic mapping disabled. Deterministic mapper used.")
            elif use_llm and not selected_model:
                messages.append("No Ollama model selected. Deterministic mapper used.")
            llm_result = None

        deterministic_plan = self.deterministic_mapper.map_request_to_plan(user_message, dataset_profile, graph_matrix)
        if dataset_profile is not None:
            deterministic_plan = self.field_mapper.propose_roles(user_message, dataset_profile, deterministic_plan)
        deterministic_plan.metadata.mapping_method = "deterministic_fallback" if attempted_llm else "deterministic"
        validation = self._validate(deterministic_plan, dataset_profile, product_kb)
        return PlanningResult(
            visual_plan=deterministic_plan,
            validation_result=validation,
            mapping_method="deterministic_fallback" if attempted_llm else "deterministic",
            llm_mapping_result=llm_result,
            used_fallback=attempted_llm,
            messages=messages,
        )

    def _validate(
        self,
        plan,
        dataset_profile: DatasetProfile | None,
        product_kb: ProductKnowledgeBase | None,
    ) -> ValidationResult:
        validation = self.visual_plan_validator.validate(plan, dataset_profile, None)
        if product_kb is not None:
            capability_result = self.capability_validator.validate_against_capabilities(plan, product_kb)
            validation.messages.extend(capability_result.messages)
        return validation
