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
    subtitle: str | None = None
    colour_scheme: str | None = None
    palette: dict[str, str] = field(default_factory=dict)
    font_family: str | None = None
    grid: str | None = None
    legend_position: str | None = None
    background: str | None = None
    plot_background: str | None = None
    diagram_direction: str | None = None
    highlights: dict[str, Any] = field(default_factory=dict)
    labels: dict[str, str] = field(default_factory=dict)
    orientation: str | None = None


@dataclass
class PlanMetadata:
    plan_id: str | None = None
    created_from: str | None = None
    mapping_method: str | None = None
    style_profile_id: str | None = None
    style_profile_name: str | None = None
    confidence: float | None = None
    assumptions: list[str] = field(default_factory=list)
    pending_questions: list[str] = field(default_factory=list)
    is_preview_stale: bool = True


@dataclass
class RenderTarget:
    renderer: str | None = None
    output_format: str | None = None


@dataclass
class DiagramNode:
    id: str
    label: str
    node_type: str = "process"


@dataclass
class DiagramEdge:
    source: str
    target: str
    label: str | None = None


@dataclass
class VisualPlan:
    visual_kind: str
    intent: str
    chart_type: str | None = None
    diagram_type: str | None = None
    data_roles: list[DataRole] = field(default_factory=list)
    filters: list[dict[str, Any]] = field(default_factory=list)
    grouping: list[str] = field(default_factory=list)
    diagram_nodes: list[DiagramNode] = field(default_factory=list)
    diagram_edges: list[DiagramEdge] = field(default_factory=list)
    style: StyleIntent = field(default_factory=StyleIntent)
    render_target: RenderTarget = field(default_factory=RenderTarget)
    metadata: PlanMetadata = field(default_factory=PlanMetadata)
    notes: list[str] = field(default_factory=list)

    @property
    def renderer(self) -> str | None:
        return self.render_target.renderer

    @renderer.setter
    def renderer(self, value: str | None) -> None:
        self.render_target.renderer = value
