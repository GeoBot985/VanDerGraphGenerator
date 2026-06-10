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
    allowed_orientations = {"vertical", "horizontal"}

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

        style = data.get("style")
        if style is not None and not isinstance(style, dict):
            result.add_error("style must be an object.")
        if isinstance(style, dict):
            orientation = style.get("orientation")
            if orientation is not None and orientation not in self.allowed_orientations:
                result.add_error(f"Unsupported orientation: {orientation}.")
            highlights = style.get("highlights")
            if highlights is not None and not isinstance(highlights, dict):
                result.add_error("style.highlights must be an object.")
            labels = style.get("labels")
            if labels is not None and not isinstance(labels, dict):
                result.add_error("style.labels must be an object.")

        if "diagram_nodes" in data and not isinstance(data.get("diagram_nodes"), list):
            result.add_error("diagram_nodes must be a list.")
        if "diagram_edges" in data and not isinstance(data.get("diagram_edges"), list):
            result.add_error("diagram_edges must be a list.")

        if visual_kind == "chart" and chart_type is None:
            result.add_error("chart draft must include chart_type.")
        if visual_kind == "diagram" and diagram_type is None:
            result.add_error("diagram draft must include diagram_type.")

        if chart_type is not None and visual_kind != "chart":
            result.add_error("chart_type only applies to chart drafts.")
        if diagram_type is not None and visual_kind != "diagram":
            result.add_error("diagram_type only applies to diagram drafts.")

        if visual_kind == "diagram":
            nodes = data.get("diagram_nodes", [])
            edges = data.get("diagram_edges", [])
            if not isinstance(nodes, list) or not nodes:
                result.add_warning("diagram drafts should include diagram_nodes.")
            if not isinstance(edges, list) or not edges:
                result.add_warning("diagram drafts should include diagram_edges.")
            for node in nodes if isinstance(nodes, list) else []:
                if not isinstance(node, dict) or not node.get("id") or not node.get("label"):
                    result.add_error("diagram_nodes entries must include id and label.")
            for edge in edges if isinstance(edges, list) else []:
                if not isinstance(edge, dict) or not edge.get("source") or not edge.get("target"):
                    result.add_error("diagram_edges entries must include source and target.")

        return result
