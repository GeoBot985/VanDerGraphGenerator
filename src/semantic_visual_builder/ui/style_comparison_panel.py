"""Style comparison panel helpers."""

from __future__ import annotations

from semantic_visual_builder.state.app_state import AppState
from semantic_visual_builder.styles.style_comparison import StyleComparisonResult


class StyleComparisonPanel:
    """Summarize style comparison results for the UI."""

    def comparison_text(self, app_state: AppState) -> str:
        results = sorted(
            app_state.style_comparison_results,
            key=lambda r: r.similarity_score,
            reverse=True,
        )
        if not results:
            return "No comparison results yet."
        lines = ["Similar styles:"]
        for index, result in enumerate(results[:5], start=1):
            reasons_text = "; ".join(result.reasons) if result.reasons else "no specific overlap"
            lines.append(
                f"{index}. {result.compared_style_name} — "
                f"{result.similarity_percent}% — {reasons_text}"
            )
        return "\n".join(lines)

    def top_match_text(self, app_state: AppState) -> str:
        results = app_state.style_comparison_results
        if not results:
            return "No comparison results."
        top = results[0]
        return (
            f"Best match: {top.compared_style_name} ({top.similarity_percent}% — {top.similarity_label})"
        )

    def action_options_text(self, app_state: AppState) -> str:
        return (
            "Actions:\n"
            "- Save as new style\n"
            "- Replace existing user style\n"
            "- Cancel"
        )

    def can_replace(self, result: StyleComparisonResult, app_state: AppState) -> bool:
        """Return True if the compared style is a user style (not built-in)."""
        from semantic_visual_builder.styles.built_in_styles import (
            list_builtin_style_profiles,
        )

        builtin_ids = {style.style_id for style in list_builtin_style_profiles()}
        return result.compared_style_id not in builtin_ids
