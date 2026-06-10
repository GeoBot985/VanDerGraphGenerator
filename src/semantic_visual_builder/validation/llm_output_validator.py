"""Validate LLM draft JSON before conversion to a visual plan."""

from __future__ import annotations

from typing import Any

from .validation_result import ValidationResult


class LlmOutputValidator:
    """Validate semantic mapping drafts."""

    allowed_visual_kinds = {"chart", "diagram"}
    allowed_chart_types = {"bar", "horizontal_bar", "line", "scatter", "pie"}
    allowed_diagram_types = {"flowchart", "sequence_diagram"}
    allowed_renderers = {"plotly", "chartjs", "mermaid"}
    rejected_renderers = {"python", "generated_python", "graphviz", "arbitrary_code"}

    def validate_draft_json(self, data: dict[str, Any]) -> ValidationResult:
        result = ValidationResult()
        for field in ("visual_kind", "intent", "roles"):
            if field not in data:
                result.add_error(f"Missing required field: {field}.")
        roles = data.get("roles")
        if roles is not None and not isinstance(roles, dict):
            result.add_error("roles must be an object.")

        visual_kind = data.get("visual_kind")
        if visual_kind is not None and visual_kind not in self.allowed_visual_kinds:
            result.add_error(f"Unsupported visual_kind: {visual_kind}.")

        chart_type = data.get("chart_type")
        if chart_type is not None and chart_type not in self.allowed_chart_types:
            result.add_error(f"Unsupported chart_type: {chart_type}.")

        diagram_type = data.get("diagram_type")
        if diagram_type is not None and diagram_type not in self.allowed_diagram_types:
            result.add_error(f"Unsupported diagram_type: {diagram_type}.")

        renderer = data.get("renderer")
        if renderer is not None:
            if renderer in self.rejected_renderers:
                result.add_error(f"Unsupported renderer: {renderer}.")
            elif renderer not in self.allowed_renderers:
                result.add_error(f"Unsupported renderer: {renderer}.")

        confidence = data.get("confidence")
        if confidence is not None:
            if isinstance(confidence, bool) or not isinstance(confidence, (int, float)) or not 0 <= float(confidence) <= 1:
                result.add_error("confidence must be numeric between 0 and 1.")

        if visual_kind == "chart" and chart_type is None:
            result.add_error("chart draft must include chart_type.")
        if visual_kind == "diagram" and diagram_type is None:
            result.add_error("diagram draft must include diagram_type.")

        if chart_type is not None and visual_kind != "chart":
            result.add_error("chart_type only applies to chart drafts.")
        if diagram_type is not None and visual_kind != "diagram":
            result.add_error("diagram_type only applies to diagram drafts.")

        return result
