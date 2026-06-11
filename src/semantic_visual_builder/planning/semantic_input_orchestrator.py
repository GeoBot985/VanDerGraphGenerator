"""Route semantic chat input through LLM-first planning and refinement."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import uuid4

from semantic_visual_builder.llm.llm_mapping_result import LlmMappingResult
from semantic_visual_builder.planning.clarification import ClarificationRequest
from semantic_visual_builder.planning.planning_orchestrator import (
    PlanningOrchestrator,
    PlanningResult,
)
from semantic_visual_builder.planning.refinement_orchestrator import (
    RefinementOrchestrator,
    RefinementResult,
)
from semantic_visual_builder.planning.semantic_trace import SemanticTrace
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
    trace: SemanticTrace | None = None


class SemanticInputOrchestrator:
    """Choose the correct semantic route without blocking LLM interpretation."""

    def __init__(
        self,
        planning_orchestrator: PlanningOrchestrator,
        refinement_orchestrator: RefinementOrchestrator,
        message_classifier: object | None = None,
    ):
        self.planning_orchestrator = planning_orchestrator
        self.refinement_orchestrator = refinement_orchestrator
        self._legacy_message_classifier = message_classifier

    def handle_message(
        self,
        user_message: str,
        app_state: AppState,
        use_llm: bool = True,
    ) -> SemanticInputResult:
        selected_model = app_state.model_registry.selected_model
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
            action = self._result_action(
                refinement_result.clarification_requests,
                refinement_result.validation_result,
                default_action="refinement_request",
            )
            return self._to_semantic_result(
                action=action,
                result=refinement_result,
                messages=messages,
                app_state=app_state,
                user_message=user_message,
                attempted_llm=attempted_llm,
                selected_model=selected_model,
            )

        planning_result = self.planning_orchestrator.create_or_update_plan(
            user_message=user_message,
            app_state=app_state,
            use_llm=use_llm,
        )
        action = self._result_action(
            planning_result.clarification_requests,
            planning_result.validation_result,
            default_action="visual_request",
        )
        return self._to_semantic_result(
            action=action,
            result=planning_result,
            messages=messages,
            app_state=app_state,
            user_message=user_message,
            attempted_llm=attempted_llm,
            selected_model=selected_model,
        )

    def process_message(
        self,
        user_message: str,
        app_state: AppState,
        use_llm: bool = True,
    ) -> SemanticInputResult:
        """Backward-compatible alias for handle_message()."""
        return self.handle_message(user_message, app_state, use_llm=use_llm)

    def _to_semantic_result(
        self,
        action: str,
        result: PlanningResult | RefinementResult,
        messages: list[str],
        app_state: AppState,
        user_message: str,
        attempted_llm: bool,
        selected_model: str | None,
    ) -> SemanticInputResult:
        llm_mapping_result = getattr(result, "llm_mapping_result", None)
        llm_success = bool(
            result.mapping_method.startswith("llm")
            and (llm_mapping_result is None or llm_mapping_result.draft is not None)
        )
        messages.append(f"LLM success: {'yes' if llm_success else 'no'}")
        messages.append(f"Fallback used: {'yes' if result.used_fallback else 'no'}")
        fallback_reason = "; ".join(result.messages) if result.messages else "none"
        if result.used_fallback:
            messages.append(f"Fallback reason: {fallback_reason}")
        elif not llm_success and result.mapping_method == "llm_rejected":
            messages.append("Validation failure: unsupported visual type.")
        messages.append(f"Mapping method: {result.mapping_method}")
        messages.extend(result.messages)
        trace = self._build_trace(
            request_id=str(uuid4()),
            created_at=datetime.now(timezone.utc).isoformat(),
            user_message=user_message,
            action=action,
            result=result,
            llm_mapping_result=llm_mapping_result,
            llm_success=llm_success,
            attempted_llm=attempted_llm,
            selected_model=selected_model,
            app_state=app_state,
            fallback_reason=fallback_reason,
        )
        app_state.set_semantic_trace(trace)
        return SemanticInputResult(
            action=action,
            visual_plan=result.visual_plan,
            validation_result=result.validation_result,
            mapping_method=result.mapping_method,
            llm_mapping_result=llm_mapping_result,
            used_fallback=result.used_fallback,
            messages=messages,
            clarification_requests=result.clarification_requests,
            trace=trace,
        )

    def _result_action(
        self,
        clarification_requests: list[ClarificationRequest],
        validation_result: ValidationResult,
        default_action: str,
    ) -> str:
        if clarification_requests:
            return "clarification_request"
        validation_messages = " ".join(
            message.message for message in validation_result.messages
        ).lower()
        if (
            "unsupported chart_type" in validation_messages
            or "unsupported diagram_type" in validation_messages
        ):
            return "unsupported"
        return default_action

    def _build_trace(
        self,
        request_id: str,
        created_at: str,
        user_message: str,
        action: str,
        result: PlanningResult | RefinementResult,
        llm_mapping_result: LlmMappingResult | None,
        llm_success: bool,
        attempted_llm: bool,
        selected_model: str | None,
        app_state: AppState,
        fallback_reason: str,
    ) -> SemanticTrace:
        validation_errors = [
            message.message
            for message in result.validation_result.messages
            if message.severity.value == "error"
        ]
        validation_warnings = [
            message.message
            for message in result.validation_result.messages
            if message.severity.value == "warning"
        ]
        plan = result.visual_plan
        return SemanticTrace(
            request_id=request_id,
            created_at=created_at,
            user_message=user_message,
            input_interpreter=(
                "llm"
                if attempted_llm
                else "deterministic_fallback"
                if result.used_fallback
                else "system"
            ),
            llm_enabled=app_state.llm_mapping_enabled,
            llm_attempted=attempted_llm,
            llm_model=selected_model,
            llm_success=llm_success,
            llm_error=(
                llm_mapping_result.errors[0]
                if llm_mapping_result and llm_mapping_result.errors
                else None
            ),
            mapping_method=result.mapping_method,
            used_fallback=result.used_fallback,
            fallback_reason=fallback_reason if result.used_fallback else None,
            graph_matrix_schema_version=(
                app_state.graph_matrix.schema_version()
                if app_state.graph_matrix is not None
                else None
            ),
            validation_success=result.validation_result.is_valid,
            validation_errors=validation_errors,
            validation_warnings=validation_warnings,
            action=action,
            visual_kind=plan.visual_kind if plan is not None else None,
            chart_type=plan.chart_type if plan is not None else None,
            diagram_type=plan.diagram_type if plan is not None else None,
            renderer=(plan.render_target.renderer if plan is not None else None),
            assumptions=(list(plan.metadata.assumptions) if plan is not None else []),
            pending_questions=(
                list(plan.metadata.pending_questions) if plan is not None else []
            ),
            raw_llm_response_available=bool(
                llm_mapping_result and llm_mapping_result.raw_response
            ),
            raw_llm_response_preview=(
                llm_mapping_result.raw_response[:500]
                if llm_mapping_result and llm_mapping_result.raw_response
                else None
            ),
        )
