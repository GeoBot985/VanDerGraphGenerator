"""Deterministic fallback patch planner for refinement requests."""

from __future__ import annotations

import re

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

        chart_type = self._extract_requested_chart_type(text)
        if chart_type is not None:
            patch.chart_type = chart_type
            if chart_type == "horizontal_bar":
                patch.style.orientation = "horizontal"
            notes.append(f"Refinement: chart type set to {chart_type}.")

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

    def _extract_requested_chart_type(self, text: str) -> str | None:
        chart_type_patterns = {
            "horizontal_bar": [
                r"\bhorizontal\s+bar\b",
                r"\bhorizontal\b",
            ],
            "stacked_bar": [
                r"\bstacked\s+bar\b",
            ],
            "box_plot": [
                r"\bbox\s+plot\b",
                r"\bboxplot\b",
            ],
            "heatmap": [
                r"\bheatmap\b",
            ],
            "histogram": [
                r"\bhistogram\b",
            ],
            "scatter": [
                r"\bscatter\b",
            ],
            "line": [
                r"\bline\s+chart\b",
                r"\bline\b",
            ],
            "pie": [
                r"\bpie\s+chart\b",
                r"\bpie\b",
                r"\bdonut\b",
            ],
            "bar": [
                r"\bbar\s+chart\b",
                r"\bbar\b",
            ],
        }
        change_verbs = r"(?:make|change|convert|switch|turn|use|set)"
        for chart_type, patterns in chart_type_patterns.items():
            for pattern in patterns:
                if re.search(rf"{change_verbs}.*{pattern}", text):
                    return chart_type
                if re.search(rf"{change_verbs}.*to.*{pattern}", text):
                    return chart_type
                if re.search(rf"{change_verbs}.*into.*{pattern}", text):
                    return chart_type
                if re.search(rf"\bto\b.*{pattern}", text):
                    return chart_type
                if re.search(rf"\binto\b.*{pattern}", text):
                    return chart_type
        return None

    def _extract_after(self, original: str, lowered: str, marker: str) -> str | None:
        index = lowered.find(marker)
        if index == -1:
            return None
        return original[index + len(marker) :].strip(" .")
