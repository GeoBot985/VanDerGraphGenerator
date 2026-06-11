"""Coordinate multi-turn visual plan refinement."""

from __future__ import annotations

from dataclasses import dataclass, field

from semantic_visual_builder.llm.llm_semantic_mapper import LlmSemanticMapper
from semantic_visual_builder.planning.clarification import ClarificationRequest
from semantic_visual_builder.planning.clarification_engine import ClarificationEngine
from semantic_visual_builder.planning.deterministic_fallback_patch_planner import (
    DeterministicFallbackPatchPlanner,
)
from semantic_visual_builder.planning.field_mapper import FieldMapper
from semantic_visual_builder.planning.visual_plan import get_role
from semantic_visual_builder.planning.visual_plan import summarize_visual_plan
from semantic_visual_builder.planning.visual_plan_patch import VisualPlanPatch
from semantic_visual_builder.planning.visual_plan_patch_applier import (
    VisualPlanPatchApplier,
)
from semantic_visual_builder.planning.visual_plan_schema import VisualPlan
from semantic_visual_builder.state.app_state import AppState
from semantic_visual_builder.validation.capability_validator import CapabilityValidator
from semantic_visual_builder.validation.validation_result import ValidationResult
from semantic_visual_builder.validation.visual_plan_validator import VisualPlanValidator


@dataclass
class RefinementResult:
    visual_plan: VisualPlan | None
    validation_result: ValidationResult
    mapping_method: str
    clarification_requests: list[ClarificationRequest] = field(default_factory=list)
    used_fallback: bool = False
    messages: list[str] = field(default_factory=list)


class RefinementOrchestrator:
    """Refine an accepted plan using LLM or deterministic fallbacks."""

    def __init__(
        self,
        llm_mapper: LlmSemanticMapper,
        deterministic_refinement_engine: object | None = None,
        field_mapper: FieldMapper | None = None,
        visual_plan_validator: VisualPlanValidator | None = None,
        capability_validator: CapabilityValidator | None = None,
        clarification_engine: ClarificationEngine | None = None,
        deterministic_fallback_patch_planner: DeterministicFallbackPatchPlanner
        | None = None,
        patch_applier: VisualPlanPatchApplier | None = None,
    ):
        self.llm_mapper = llm_mapper
        self.deterministic_refinement_engine = deterministic_refinement_engine
        self.field_mapper = field_mapper or FieldMapper()
        self.deterministic_fallback_patch_planner = (
            deterministic_fallback_patch_planner or DeterministicFallbackPatchPlanner()
        )
        self.patch_applier = patch_applier or VisualPlanPatchApplier()
        self.visual_plan_validator = visual_plan_validator or VisualPlanValidator()
        self.capability_validator = capability_validator or CapabilityValidator()
        self.clarification_engine = clarification_engine or ClarificationEngine()

    def refine_plan(
        self,
        current_plan: VisualPlan,
        user_message: str,
        app_state: AppState,
        use_llm: bool = True,
    ) -> RefinementResult:
        dataset_profile = app_state.dataset_context.profile
        product_kb = app_state.product_kb
        graph_matrix = app_state.graph_matrix
        selected_model = app_state.model_registry.selected_model
        messages: list[str] = []
        llm_result = None
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
                current_plan_summary=summarize_visual_plan(current_plan),
                current_plan=current_plan,
            )
            if llm_result.draft is not None:
                refined = self.patch_applier.apply_patch(
                    current_plan, VisualPlanPatch.from_llm_draft(llm_result.draft)
                )
                if dataset_profile is not None and self._needs_field_completion(refined):
                    completed_refined = self.field_mapper.complete_missing_roles(
                        user_message, dataset_profile, refined
                    )
                    if completed_refined != refined:
                        refined = completed_refined
                        messages.append(
                            "Completed missing LLM role fields with deterministic "
                            "field mapping."
                        )
                refined.metadata.mapping_method = (
                    "llm_with_repair" if llm_result.used_repair else "llm"
                )
                validation = self._validate(
                    refined, dataset_profile, product_kb, graph_matrix
                )
                clarification_requests = (
                    self.clarification_engine.detect_needed_clarification(
                        refined, dataset_profile
                    )
                )
                if validation.is_valid and not clarification_requests:
                    refined.metadata.is_preview_stale = True
                    return RefinementResult(
                        visual_plan=refined,
                        validation_result=validation,
                        mapping_method=refined.metadata.mapping_method or "llm",
                        used_fallback=False,
                        messages=messages,
                    )
                if not clarification_requests:
                    clarification_requests = self._clarification_from_validation(
                        refined, validation, dataset_profile
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
                    return RefinementResult(
                        visual_plan=None,
                        validation_result=validation,
                        mapping_method="llm_rejected",
                        used_fallback=False,
                        messages=messages,
                    )
                messages.extend(message.message for message in validation.messages)
                messages.append(
                    "Refined plan requires clarification before it can replace "
                    "the current plan."
                )
                return RefinementResult(
                    visual_plan=None,
                    validation_result=validation,
                    mapping_method=refined.metadata.mapping_method or "llm",
                    clarification_requests=clarification_requests,
                    used_fallback=False,
                    messages=messages,
                )
            messages.extend(llm_result.errors or ["LLM refinement failed."])
            messages.append("The LLM response did not pass the graph matrix contract.")
            messages.append(
                "I used deterministic fallback patch planning where possible."
            )
        else:
            if use_llm and not app_state.llm_mapping_enabled:
                messages.append(
                    "I could not use LLM semantic refinement because it is "
                    "disabled. I used deterministic fallback patch planning "
                    "where possible."
                )
            elif use_llm and not selected_model:
                messages.append(
                    "I could not use LLM semantic refinement because no model "
                    "is selected. I used deterministic fallback patch planning "
                    "where possible."
                )

        if hasattr(self.deterministic_fallback_patch_planner, "build_patch"):
            patch = self.deterministic_fallback_patch_planner.build_patch(
                current_plan, user_message
            )
        elif hasattr(self.deterministic_refinement_engine, "apply_refinement"):
            refined_plan = self.deterministic_refinement_engine.apply_refinement(
                current_plan, user_message
            )
            patch = self._patch_from_plan(current_plan, refined_plan)
        else:
            patch = VisualPlanPatch()
        refined = self.patch_applier.apply_patch(current_plan, patch)
        refined.metadata.mapping_method = "deterministic_fallback"
        validation = self._validate(refined, dataset_profile, product_kb, graph_matrix)
        clarification_requests = self.clarification_engine.detect_needed_clarification(
            refined, dataset_profile
        )
        if validation.is_valid and not clarification_requests:
            refined.metadata.is_preview_stale = True
            return RefinementResult(
                visual_plan=refined,
                validation_result=validation,
                mapping_method=refined.metadata.mapping_method
                or "deterministic_fallback",
                used_fallback=True,
                messages=messages,
            )
        if not clarification_requests:
            clarification_requests = self._clarification_from_validation(
                refined, validation, dataset_profile
            )
        messages.extend(message.message for message in validation.messages)
        messages.append(
            "Deterministic refinement requires clarification before it can "
            "replace the current plan."
        )
        return RefinementResult(
            visual_plan=None,
            validation_result=validation,
            mapping_method=refined.metadata.mapping_method or "deterministic_fallback",
            clarification_requests=clarification_requests,
            used_fallback=True,
            messages=messages,
        )

    def _validate(
        self, plan: VisualPlan, dataset_profile, product_kb, graph_matrix
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

    def _clarification_from_validation(
        self,
        plan: VisualPlan,
        validation: ValidationResult,
        dataset_profile,
    ) -> list[ClarificationRequest]:
        if not validation.messages:
            return []
        message = validation.messages[0].message
        return [
            ClarificationRequest(
                question=message,
                reason=message,
                field_name="category" if plan.visual_kind == "chart" else None,
            )
        ]

    def _patch_from_plan(
        self, base: VisualPlan, updated: VisualPlan
    ) -> VisualPlanPatch:
        style = None
        if updated.style != base.style:
            style = updated.style
        render_target = None
        if updated.render_target != base.render_target:
            render_target = updated.render_target
        notes = updated.notes if updated.notes != base.notes else None
        data_roles = (
            updated.data_roles if updated.data_roles != base.data_roles else None
        )
        filters = updated.filters if updated.filters != base.filters else None
        grouping = updated.grouping if updated.grouping != base.grouping else None
        diagram_nodes = (
            updated.diagram_nodes
            if updated.diagram_nodes != base.diagram_nodes
            else None
        )
        diagram_edges = (
            updated.diagram_edges
            if updated.diagram_edges != base.diagram_edges
            else None
        )
        return VisualPlanPatch(
            visual_kind=updated.visual_kind
            if updated.visual_kind != base.visual_kind
            else None,
            intent=updated.intent if updated.intent != base.intent else None,
            chart_type=updated.chart_type
            if updated.chart_type != base.chart_type
            else None,
            diagram_type=updated.diagram_type
            if updated.diagram_type != base.diagram_type
            else None,
            data_roles=data_roles,
            filters=filters,
            grouping=grouping,
            diagram_nodes=diagram_nodes,
            diagram_edges=diagram_edges,
            style=style,
            render_target=render_target,
            notes=notes,
        )

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
