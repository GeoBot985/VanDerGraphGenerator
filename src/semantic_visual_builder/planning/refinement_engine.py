"""Apply deterministic refinements to visual plans."""

from __future__ import annotations

from .visual_plan import clone_visual_plan
from .visual_plan_schema import VisualPlan


class RefinementEngine:
    """Update a plan based on simple text refinements."""

    def apply_refinement(self, current_plan: VisualPlan, message: str) -> VisualPlan:
        updated = clone_visual_plan(current_plan)
        text = message.lower().strip()

        if "make it a bar chart" in text or "make it bar chart" in text:
            updated.chart_type = "bar"
            updated.notes.append("Refinement: chart type set to bar.")
        elif "make it a line chart" in text:
            updated.chart_type = "line"
            updated.notes.append("Refinement: chart type set to line.")
        elif "make it horizontal" in text:
            updated.chart_type = "horizontal_bar"
            updated.style.orientation = "horizontal"
            updated.notes.append("Refinement: chart type set to horizontal_bar.")
        elif "use pie chart" in text:
            updated.chart_type = "pie"
            updated.notes.append("Refinement: chart type set to pie.")

        title = self._extract_after(message, text, "title should be")
        if title is None:
            title = self._extract_after(message, text, "change title to")
        if title:
            updated.style.title = title
            updated.notes.append(f"Refinement: title set to {title}.")

        if "highlight" in text:
            value = self._extract_after(message, text, "highlight")
            if value:
                highlight = {"value": value}
                if any(keyword in text for keyword in ("failed", "approved", "rejected", "pending")):
                    highlight["field"] = "Status"
                updated.style.highlights = highlight
                updated.notes.append(f"Refinement: highlighted {value}.")

        for colour in ("green", "blue", "red", "corporate blue"):
            if colour in text:
                updated.style.colour_scheme = colour
                updated.notes.append(f"Refinement: colour scheme set to {colour}.")
                break

        return updated

    def _extract_after(self, original: str, lowered: str, marker: str) -> str | None:
        index = lowered.find(marker)
        if index == -1:
            return None
        return original[index + len(marker) :].strip(" .")
