"""Status panel helpers."""

from __future__ import annotations

from semantic_visual_builder.state.app_state import AppState


class StatusPanel:
    def status_text(self, app_state: AppState) -> str:
        ollama_connected = (
            app_state.ollama_status.is_connected if app_state.ollama_status else False
        )
        dataset_loaded = (
            "Loaded"
            if app_state.dataset_context.loaded_dataset
            else "No dataset loaded"
        )
        plan_status = (
            "Available" if app_state.current_visual_plan else "No visual plan"
        )
        lines = [
            f"Ollama status: {ollama_connected}",
            f"Selected model: {app_state.model_registry.selected_model or 'None'}",
            f"Dataset status: {dataset_loaded}",
            f"Plan status: {plan_status}",
            f"Preview status: {app_state.preview_status or 'No preview status'}",
            f"Recipe status: {app_state.active_recipe_name or 'No active recipe'}",
        ]
        if app_state.last_semantic_trace is not None:
            trace = app_state.last_semantic_trace
            lines.extend(
                [
                    "",
                    f"Request ID: {trace.request_id}",
                    f"Interpreter: {trace.input_interpreter}",
                    f"LLM attempted: {'yes' if trace.llm_attempted else 'no'}",
                    f"LLM success: {'yes' if trace.llm_success else 'no'}",
                    f"Mapping method: {trace.mapping_method or 'None'}",
                    f"Fallback used: {'yes' if trace.used_fallback else 'no'}",
                    (
                        "Graph matrix version: "
                        f"{trace.graph_matrix_schema_version or 'None'}"
                    ),
                    (
                        "Validation success: "
                        f"{'yes' if trace.validation_success else 'no'}"
                    ),
                    f"Action: {trace.action or 'None'}",
                    f"Visual kind: {trace.visual_kind or 'None'}",
                    f"Chart type: {trace.chart_type or 'None'}",
                    f"Diagram type: {trace.diagram_type or 'None'}",
                    f"Renderer: {trace.renderer or 'None'}",
                ]
            )
            if trace.fallback_reason:
                lines.append(f"Fallback reason: {trace.fallback_reason}")
        return "\n".join(lines)
