"""Style panel helpers."""

from __future__ import annotations

from semantic_visual_builder.state.app_state import AppState
from semantic_visual_builder.styles.style_summary import summarize_style


class StylePanel:
    def active_style_text(self, app_state: AppState) -> str:
        style = app_state.active_style_profile
        if style is None:
            return "Active style: none"
        lines = [f"Active style: {style.style_name}", f"ID: {style.style_id}"]
        result = app_state.style_application_result
        if result is not None:
            lines.append(f"Application status: {'success' if result.success else 'failed'}")
        return "\n".join(lines)

    def available_styles_text(self, app_state: AppState) -> str:
        if not app_state.available_style_profiles:
            return "Available styles: none"
        return "\n".join(
            ["Available styles:"]
            + [f"- {style.style_name} ({style.style_id})" for style in app_state.available_style_profiles]
        )

    def summary_text(self, app_state: AppState) -> str:
        style = app_state.active_style_profile
        return summarize_style(style) if style is not None else "No style selected."
