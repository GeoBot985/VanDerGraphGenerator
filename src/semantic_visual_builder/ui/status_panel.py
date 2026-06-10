"""Status panel helpers."""

from __future__ import annotations

from semantic_visual_builder.state.app_state import AppState


class StatusPanel:
    def status_text(self, app_state: AppState) -> str:
        lines = [
            f"Ollama status: {app_state.ollama_status.is_connected if app_state.ollama_status else False}",
            f"Selected model: {app_state.model_registry.selected_model or 'None'}",
            f"Dataset status: {'Loaded' if app_state.dataset_context.loaded_dataset else 'No dataset loaded'}",
            f"Plan status: {'Available' if app_state.current_visual_plan else 'No visual plan'}",
            f"Preview status: {app_state.preview_status or 'No preview status'}",
            f"Recipe status: {app_state.active_recipe_name or 'No active recipe'}",
        ]
        return "\n".join(lines)
