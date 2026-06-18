"""Style panel helpers."""

from __future__ import annotations

from semantic_visual_builder.state.app_state import AppState
from semantic_visual_builder.styles.built_in_styles import list_builtin_style_profiles
from semantic_visual_builder.styles.style_summary import summarize_style

_BUILTIN_STYLE_IDS = frozenset(
    style.style_id for style in list_builtin_style_profiles()
)


class StylePanel:
    def active_style_text(self, app_state: AppState) -> str:
        style = app_state.active_style_profile
        if style is None:
            return "Active style: none"
        kind = "built-in" if style.style_id in _BUILTIN_STYLE_IDS else "user"
        lines = [
            f"Active style: {style.style_name}",
            f"ID: {style.style_id}",
            f"Type: {kind}",
        ]
        result = app_state.style_application_result
        if result is not None:
            lines.append(
                f"Application status: {'success' if result.success else 'failed'}"
            )
        recipe = app_state.active_recipe
        if recipe is not None and recipe.metadata.default_style_profile_id == style.style_id:
            lines.append(f"Recipe default: yes (recipe: {recipe.recipe_name})")
        return "\n".join(lines)

    def available_styles_text(self, app_state: AppState) -> str:
        if not app_state.available_style_profiles:
            return "Available styles: none"
        lines = ["Available styles:"]
        for style in app_state.available_style_profiles:
            kind = "built-in" if style.style_id in _BUILTIN_STYLE_IDS else "user"
            lines.append(f"- {style.style_name} ({style.style_id}) [{kind}]")
        return "\n".join(lines)

    def summary_text(self, app_state: AppState) -> str:
        style = app_state.active_style_profile
        return summarize_style(style) if style is not None else "No style selected."

    def import_export_text(self, app_state: AppState) -> str:
        lines: list[str] = []
        if app_state.last_imported_style_path:
            lines.append(f"Last imported: {app_state.last_imported_style_path}")
        if app_state.last_exported_style_path:
            lines.append(f"Last exported: {app_state.last_exported_style_path}")
        return "\n".join(lines) if lines else "No import/export activity."

    def recipe_default_text(self, app_state: AppState) -> str:
        recipe = app_state.active_recipe
        if recipe is None:
            return "No active recipe."
        default_id = recipe.metadata.default_style_profile_id
        if not default_id:
            return f"Recipe '{recipe.recipe_name}' has no default style."
        name = recipe.metadata.default_style_profile_name or default_id
        return f"Recipe default style: {name} ({default_id})"
