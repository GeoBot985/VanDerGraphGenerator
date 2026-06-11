"""Route semantic chat input through LLM-first planning and refinement."""

from __future__ import annotations

from dataclasses import dataclass, field

from semantic_visual_builder.llm.llm_mapping_result import LlmMappingResult
from semantic_visual_builder.planning.clarification import ClarificationRequest
from semantic_visual_builder.planning.message_classifier import (
    MessageClassifier,
    MessageIntent,
)
from semantic_visual_builder.planning.planning_orchestrator import (
    PlanningOrchestrator,
    PlanningResult,
)
from semantic_visual_builder.planning.refinement_orchestrator import (
    RefinementOrchestrator,
    RefinementResult,
)
from semantic_visual_builder.planning.visual_plan_schema import VisualPlan
from semantic_visual_builder.state.app_state import AppState
from semantic_visual_builder.validation.validation_result import ValidationResult


@dataclass
class SemanticInputResult:
    action: str
    visual_plan: VisualPlan | None
    validation_result: ValidationResult
    mapping_method: str
    llm_mapping_result: LlmMappingResult | None = None
    used_fallback: bool = False
    messages: list[str] = field(default_factory=list)
    clarification_requests: list[ClarificationRequest] = field(default_factory=list)


class SemanticInputOrchestrator:
    """Choose the correct semantic route without blocking LLM interpretation."""

    def __init__(
        self,
        planning_orchestrator: PlanningOrchestrator,
        refinement_orchestrator: RefinementOrchestrator,
        message_classifier: MessageClassifier | None = None,
    ):
        self.planning_orchestrator = planning_orchestrator
        self.refinement_orchestrator = refinement_orchestrator
        self.message_classifier = message_classifier or MessageClassifier()

    def process_message(
        self,
        user_message: str,
        app_state: AppState,
        use_llm: bool = True,
    ) -> SemanticInputResult:
        selected_model = app_state.model_registry.selected_model
        intent = self.message_classifier.classify(
            user_message,
            has_current_plan=app_state.current_visual_plan is not None,
        )
        if intent == MessageIntent.CAPABILITY_QUESTION:
            messages = [
                f"Selected model: {selected_model or 'None'}",
                "LLM attempted: no",
            ]
            messages.append("Semantic input action: capability_question")
            messages.append("LLM success: no")
            messages.append("Fallback used: no")
            messages.append("Mapping method: not_applicable")
            return SemanticInputResult(
                action=MessageIntent.CAPABILITY_QUESTION.value,
                visual_plan=None,
                validation_result=ValidationResult(),
                mapping_method="not_applicable",
                messages=messages,
            )
        if intent == MessageIntent.WORKFLOW_HELP:
            messages = [
                f"Selected model: {selected_model or 'None'}",
                "LLM attempted: no",
            ]
            messages.append("Semantic input action: workflow_help")
            messages.append("LLM success: no")
            messages.append("Fallback used: no")
            messages.append("Mapping method: not_applicable")
            return SemanticInputResult(
                action=MessageIntent.WORKFLOW_HELP.value,
                visual_plan=None,
                validation_result=ValidationResult(),
                mapping_method="not_applicable",
                messages=messages,
            )

        attempted_llm = bool(
            use_llm and app_state.llm_mapping_enabled and selected_model
        )
        messages = [
            f"Selected model: {selected_model or 'None'}",
            f"LLM attempted: {'yes' if attempted_llm else 'no'}",
        ]

        if app_state.current_visual_plan is not None:
            refinement_result = self.refinement_orchestrator.refine_plan(
                current_plan=app_state.current_visual_plan,
                user_message=user_message,
                app_state=app_state,
                use_llm=use_llm,
            )
            return self._to_semantic_result(
                action="clarification_request"
                if refinement_result.clarification_requests
                else MessageIntent.REFINEMENT_REQUEST.value,
                result=refinement_result,
                messages=messages,
            )

        planning_result = self.planning_orchestrator.create_or_update_plan(
            user_message=user_message,
            app_state=app_state,
            use_llm=use_llm,
        )
        return self._to_semantic_result(
            action="clarification_request"
            if planning_result.clarification_requests
            else MessageIntent.VISUAL_REQUEST.value,
            result=planning_result,
            messages=messages,
        )

    def _to_semantic_result(
        self,
        action: str,
        result: PlanningResult | RefinementResult,
        messages: list[str],
    ) -> SemanticInputResult:
        llm_mapping_result = getattr(result, "llm_mapping_result", None)
        llm_success = bool(
            result.mapping_method.startswith("llm")
            and not result.used_fallback
            and (llm_mapping_result is None or llm_mapping_result.draft is not None)
        )
        messages.append(f"LLM success: {'yes' if llm_success else 'no'}")
        messages.append(f"Fallback used: {'yes' if result.used_fallback else 'no'}")
        if result.used_fallback or (result.messages and not llm_success):
            fallback_reason = "; ".join(result.messages) if result.messages else "none"
            messages.append(f"Fallback reason: {fallback_reason}")
        messages.append(f"Mapping method: {result.mapping_method}")
        messages.extend(result.messages)
        return SemanticInputResult(
            action=action,
            visual_plan=result.visual_plan,
            validation_result=result.validation_result,
            mapping_method=result.mapping_method,
            llm_mapping_result=llm_mapping_result,
            used_fallback=result.used_fallback,
            messages=messages,
            clarification_requests=result.clarification_requests,
        )
