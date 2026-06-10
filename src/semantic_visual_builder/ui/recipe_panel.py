"""Recipe panel helpers."""

from __future__ import annotations

from semantic_visual_builder.state.app_state import AppState


class RecipePanel:
    """Summarize active recipe state for the UI."""

    def active_recipe_text(self, app_state: AppState) -> str:
        name = app_state.active_recipe_name or "No active recipe"
        path = str(app_state.active_recipe_path) if app_state.active_recipe_path else "No active recipe path"
        return f"Active recipe: {name}\nPath: {path}"

    def compatibility_text(self, app_state: AppState) -> str:
        result = app_state.recipe_compatibility_result
        if result is None:
            return "Compatibility: not checked"
        if not result.messages:
            return "Compatibility: valid"
        lines = ["Compatibility report:"]
        for message in result.messages:
            lines.append(f"- {message.severity.value.upper()}: {message.message}")
        return "\n".join(lines)
