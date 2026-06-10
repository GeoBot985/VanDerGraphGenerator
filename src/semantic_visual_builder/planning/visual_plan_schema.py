"""Neutral visual plan schema."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class DataRole:
    role: str
    field: str | None = None
    transform: str | None = None
    aggregation: str | None = None


@dataclass
class StyleIntent:
    title: str | None = None
    colour_scheme: str | None = None
    highlights: dict[str, Any] = field(default_factory=dict)
    labels: dict[str, str] = field(default_factory=dict)


@dataclass
class RenderTarget:
    renderer: str | None = None
    output_format: str | None = None


@dataclass
class VisualPlan:
    visual_kind: str
    intent: str
    chart_type: str | None = None
    diagram_type: str | None = None
    data_roles: list[DataRole] = field(default_factory=list)
    filters: list[dict[str, Any]] = field(default_factory=list)
    grouping: list[str] = field(default_factory=list)
    style: StyleIntent = field(default_factory=StyleIntent)
    render_target: RenderTarget = field(default_factory=RenderTarget)
    notes: list[str] = field(default_factory=list)

    @property
    def renderer(self) -> str | None:
        return self.render_target.renderer

    @renderer.setter
    def renderer(self, value: str | None) -> None:
        self.render_target.renderer = value
