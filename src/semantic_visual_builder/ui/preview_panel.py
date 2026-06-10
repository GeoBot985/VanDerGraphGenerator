"""Preview panel helpers."""

from __future__ import annotations

from semantic_visual_builder.state.app_state import AppState


class PreviewPanel:
    """Derive user-facing preview status text from app state."""

    def preview_status_text(self, app_state: AppState) -> str:
        if app_state.current_visual_plan is None:
            return "No visual plan yet."
        if app_state.preview_status == "Preview failed.":
            return "Preview failed."
        if app_state.current_visual_plan.metadata.is_preview_stale or app_state.preview_status == "Preview stale. Regenerate to reflect latest plan.":
            return "Preview stale. Regenerate to reflect latest plan."
        if app_state.last_preview_path is None:
            return "Visual plan ready. Preview not generated."
        if app_state.preview_status:
            return app_state.preview_status
        return "Preview generated."

    def renderer_name_text(self, app_state: AppState) -> str:
        if app_state.last_renderer_output is None:
            return "Renderer: none"
        return f"Renderer: {app_state.last_renderer_output.renderer_name}"
