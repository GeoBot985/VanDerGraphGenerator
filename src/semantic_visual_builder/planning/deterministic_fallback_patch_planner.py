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

        background_colour = self._extract_background_colour(text)
        if background_colour is not None:
            patch.style.background = background_colour
            patch.style.plot_background = background_colour
            notes.append(f"Refinement: background set to {background_colour}.")

        series_colour = self._extract_series_colour(text)
        if series_colour is not None:
            patch.style.palette = {"primary": series_colour}
            notes.append(f"Refinement: series colour set to {series_colour}.")

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

    def _extract_background_colour(self, text: str) -> str | None:
        background_patterns = (
            r"\bbackground(?:\s+colour|\s+color)?\s+(?:to\s+)?([a-z ]+)",
            r"\bmake\s+the\s+background\s+([a-z ]+)",
        )
        for pattern in background_patterns:
            match = re.search(pattern, text)
            if match:
                requested = match.group(1).strip().rstrip(".")
                resolved = self._resolve_colour(requested)
                if resolved is not None:
                    return resolved
        return None

    def _extract_series_colour(self, text: str) -> str | None:
        series_patterns = (
            r"\b(?:bar|bars|column|columns|slice|slices|series|line|lines|point|points)\s+(?:to\s+)?([a-z ]+)",
            r"\b(?:bar|bars|column|columns|slice|slices|series|line|lines|point|points)\s+(?:colour|color)\s+(?:to\s+)?([a-z ]+)",
            r"\bmake\s+the\s+(?:bar|bars|column|columns|slice|slices|series|line|lines|point|points)\s+([a-z ]+)",
            r"\bset\s+(?:the\s+)?(?:bar|bars|column|columns|slice|slices|series|line|lines|point|points)\s+(?:colour|color)\s+to\s+([a-z ]+)",
        )
        for pattern in series_patterns:
            match = re.search(pattern, text)
            if match:
                requested = match.group(1).strip().rstrip(".")
                resolved = self._resolve_colour(requested)
                if resolved is not None:
                    return resolved
        return None

    def _resolve_colour(self, requested: str) -> str | None:
        colour_map = {
            "light green": "#90ee90",
            "green": "#54A24B",
            "dark green": "#2f6b2f",
            "light blue": "#add8e6",
            "blue": "#4C78A8",
            "dark blue": "#1f4e79",
            "light grey": "#d3d3d3",
            "light gray": "#d3d3d3",
            "dark grey": "#333333",
            "dark gray": "#333333",
            "grey": "#808080",
            "gray": "#808080",
            "light red": "#f28b82",
            "red": "#e45756",
            "yellow": "#f2cf5b",
            "light yellow": "#f7e59c",
            "white": "#ffffff",
            "black": "#111111",
        }
        for name, value in colour_map.items():
            if requested.startswith(name):
                return value
        if re.fullmatch(r"#[0-9a-f]{6}", requested):
            return requested
        return None
