"""Coordinate multi-turn visual plan refinement."""

from __future__ import annotations

from dataclasses import dataclass, field

from semantic_visual_builder.llm.llm_semantic_mapper import LlmSemanticMapper
from semantic_visual_builder.planning.clarification import ClarificationRequest, PendingClarification
from semantic_visual_builder.planning.clarification_engine import ClarificationEngine
from semantic_visual_builder.planning.refinement_engine import RefinementEngine
from semantic_visual_builder.planning.visual_plan import merge_visual_plans, summarize_visual_plan, visual_plan_from_llm_draft
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
        deterministic_refinement_engine: RefinementEngine,
        visual_plan_validator: VisualPlanValidator,
        capability_validator: CapabilityValidator,
        clarification_engine: ClarificationEngine,
    ):
        self.llm_mapper = llm_mapper
        self.deterministic_refinement_engine = deterministic_refinement_engine
        self.visual_plan_validator = visual_plan_validator
        self.capability_validator = capability_validator
        self.clarification_engine = clarification_engine

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
        attempted_llm = bool(use_llm and app_state.llm_mapping_enabled and selected_model)

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
                refined = merge_visual_plans(current_plan, visual_plan_from_llm_draft(llm_result.draft))
                refined.metadata.mapping_method = "llm_with_repair" if llm_result.used_repair else "llm"
                validation = self._validate(refined, dataset_profile, product_kb)
                clarification_requests = self.clarification_engine.detect_needed_clarification(refined, dataset_profile)
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
                    clarification_requests = self._clarification_from_validation(refined, validation, dataset_profile)
                messages.extend(message.message for message in validation.messages)
                messages.append("Refined plan requires clarification before it can replace the current plan.")
                return RefinementResult(
                    visual_plan=None,
                    validation_result=validation,
                    mapping_method=refined.metadata.mapping_method or "llm",
                    clarification_requests=clarification_requests,
                    used_fallback=False,
                    messages=messages,
                )
            messages.extend(llm_result.errors or ["LLM refinement failed."])
            messages.append("LLM refinement failed. Falling back to deterministic refinement.")
        else:
            if use_llm and not app_state.llm_mapping_enabled:
                messages.append("LLM semantic mapping disabled. Deterministic refinement used.")
            elif use_llm and not selected_model:
                messages.append("No Ollama model selected. Deterministic refinement used.")

        refined = self.deterministic_refinement_engine.apply_refinement(current_plan, user_message)
        refined.metadata.mapping_method = "deterministic_fallback" if attempted_llm else "deterministic"
        validation = self._validate(refined, dataset_profile, product_kb)
        clarification_requests = self.clarification_engine.detect_needed_clarification(refined, dataset_profile)
        if validation.is_valid and not clarification_requests:
            refined.metadata.is_preview_stale = True
            return RefinementResult(
                visual_plan=refined,
                validation_result=validation,
                mapping_method=refined.metadata.mapping_method or "deterministic",
                used_fallback=attempted_llm,
                messages=messages,
            )
        if not clarification_requests:
            clarification_requests = self._clarification_from_validation(refined, validation, dataset_profile)
        messages.extend(message.message for message in validation.messages)
        messages.append("Deterministic refinement requires clarification before it can replace the current plan.")
        return RefinementResult(
            visual_plan=None,
            validation_result=validation,
            mapping_method=refined.metadata.mapping_method or "deterministic",
            clarification_requests=clarification_requests,
            used_fallback=attempted_llm,
            messages=messages,
        )

    def _validate(self, plan: VisualPlan, dataset_profile, product_kb) -> ValidationResult:
        validation = self.visual_plan_validator.validate(plan, dataset_profile, None)
        if product_kb is not None:
            capability_result = self.capability_validator.validate_against_capabilities(plan, product_kb)
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
