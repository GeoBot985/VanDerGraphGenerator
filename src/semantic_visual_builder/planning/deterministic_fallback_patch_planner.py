"""Deterministic fallback patch planner for refinement requests."""

from __future__ import annotations

from .visual_plan import clone_visual_plan
from .visual_plan_patch import VisualPlanPatch
from .visual_plan_schema import StyleIntent, VisualPlan


class DeterministicFallbackPatchPlanner:
    """Build structured refinement patches from a limited fallback lexicon."""

    def build_patch(self, current_plan: VisualPlan, message: str) -> VisualPlanPatch:
        _ = clone_visual_plan(current_plan)
        text = message.lower().strip()

        patch = VisualPlanPatch(style=StyleIntent())
        notes: list[str] = []

        if "make it a bar chart" in text or "make it bar chart" in text:
            patch.chart_type = "bar"
            notes.append("Refinement: chart type set to bar.")
        elif "make it a line chart" in text:
            patch.chart_type = "line"
            notes.append("Refinement: chart type set to line.")
        elif "make it horizontal" in text:
            patch.chart_type = "horizontal_bar"
            patch.style.orientation = "horizontal"
            notes.append("Refinement: chart type set to horizontal_bar.")
        elif "use pie chart" in text or "turn this into a pie" in text:
            patch.chart_type = "pie"
            notes.append("Refinement: chart type set to pie.")

        title = self._extract_after(message, text, "title should be")
        if title is None:
            title = self._extract_after(message, text, "change title to")
        if title:
            patch.style.title = title
            notes.append(f"Refinement: title set to {title}.")

        if "highlight" in text:
            value = self._extract_after(message, text, "highlight")
            if value:
                patch.style.highlights = {"value": value}
                notes.append(f"Refinement: highlighted {value}.")

        for colour in ("green", "blue", "red", "corporate blue"):
            if colour in text:
                patch.style.colour_scheme = colour
                notes.append(f"Refinement: colour scheme set to {colour}.")
                break

        patch.notes = notes or None
        return patch

    def _extract_after(self, original: str, lowered: str, marker: str) -> str | None:
        index = lowered.find(marker)
        if index == -1:
            return None
        return original[index + len(marker) :].strip(" .")
