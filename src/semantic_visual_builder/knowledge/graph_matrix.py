"""Graph matrix loading helpers."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from semantic_visual_builder.utils.json_utils import load_json


@dataclass
class GraphMatrix:
    """Structured graph matrix data."""

    raw: dict[str, Any]

    def schema_version(self) -> str | None:
        value = self.raw.get("schema_version")
        return str(value) if value is not None else None

    def visual_kinds(self) -> list[str]:
        return [
            str(item)
            for item in self.raw.get("visual_kinds", [])
            if isinstance(item, str)
        ]

    def roles(self) -> dict[str, dict[str, Any]]:
        roles = self.raw.get("roles", {})
        return roles if isinstance(roles, dict) else {}

    def chart_types(self) -> dict[str, dict[str, Any]]:
        chart_types = self.raw.get("chart_types", {})
        return chart_types if isinstance(chart_types, dict) else {}

    def diagram_types(self) -> dict[str, dict[str, Any]]:
        diagram_types = self.raw.get("diagram_types", {})
        return diagram_types if isinstance(diagram_types, dict) else {}

    def allowed_aggregations(self) -> list[str]:
        return [
            str(item)
            for item in self.raw.get("allowed_aggregations", [])
            if isinstance(item, str)
        ]

    def allowed_transforms(self) -> list[str]:
        return [
            str(item)
            for item in self.raw.get("allowed_transforms", [])
            if isinstance(item, str)
        ]

    def allowed_filter_operators(self) -> list[str]:
        return [
            str(item)
            for item in self.raw.get("allowed_filter_operators", [])
            if isinstance(item, str)
        ]

    def list_intents(self) -> list[str]:
        return [
            item.get("intent", "")
            for item in self.raw.get("intents", [])
            if isinstance(item, dict) and item.get("intent")
        ]

    def supported_chart_types(self) -> list[str]:
        return list(self.chart_types().keys())

    def supported_diagram_types(self) -> list[str]:
        return list(self.diagram_types().keys())

    def get_visual_spec(self, visual_type: str) -> dict[str, Any] | None:
        if visual_type in self.chart_types():
            return self.chart_types()[visual_type]
        if visual_type in self.diagram_types():
            return self.diagram_types()[visual_type]
        return None

    def renderer_allowed(self, visual_type: str, renderer: str | None) -> bool:
        if renderer is None:
            return False
        spec = self.get_visual_spec(visual_type)
        if spec is None:
            return False
        allowed_renderers = spec.get("allowed_renderers", [])
        return isinstance(allowed_renderers, list) and renderer in allowed_renderers

    def required_roles_for(self, visual_type: str) -> list[str]:
        spec = self.get_visual_spec(visual_type)
        if spec is None:
            return []
        required_roles = spec.get("required_roles", [])
        return [str(item) for item in required_roles if isinstance(item, str)]

    def allowed_roles_for(self, visual_type: str) -> list[str]:
        spec = self.get_visual_spec(visual_type)
        if spec is None:
            return []
        allowed_roles = spec.get("allowed_roles")
        if isinstance(allowed_roles, list):
            return [str(item) for item in allowed_roles if isinstance(item, str)]
        required = self.required_roles_for(visual_type)
        optional_roles = spec.get("optional_roles", [])
        optional = (
            [str(item) for item in optional_roles if isinstance(item, str)]
            if isinstance(optional_roles, list)
            else []
        )
        return required + [item for item in optional if item not in required]


class GraphMatrixLoader:
    """Load the graph matrix seed file."""

    def __init__(self, matrix_path: Path):
        self.matrix_path = matrix_path

    def load(self) -> GraphMatrix:
        return GraphMatrix(raw=load_json(self.matrix_path))
