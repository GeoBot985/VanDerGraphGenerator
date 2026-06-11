"""Structured visual plan patch objects."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from semantic_visual_builder.llm.llm_mapping_result import LlmVisualPlanDraft

from .visual_plan import normalise_style_colour
from .visual_plan_schema import (
    DataRole,
    DiagramEdge,
    DiagramNode,
    RenderTarget,
    StyleIntent,
)


@dataclass
class VisualPlanPatch:
    visual_kind: str | None = None
    intent: str | None = None
    chart_type: str | None = None
    diagram_type: str | None = None
    data_roles: list[DataRole] | None = None
    filters: list[dict[str, Any]] | None = None
    grouping: list[str] | None = None
    diagram_nodes: list[DiagramNode] | None = None
    diagram_edges: list[DiagramEdge] | None = None
    style: StyleIntent | None = None
    render_target: RenderTarget | None = None
    notes: list[str] | None = None

    @classmethod
    def from_llm_draft(cls, draft: LlmVisualPlanDraft) -> "VisualPlanPatch":
        style_data = draft.style or {}
        style = StyleIntent(
            title=style_data.get("title"),
            subtitle=style_data.get("subtitle"),
            colour_scheme=style_data.get("colour_scheme"),
            palette=style_data.get("palette", {}) or {},
            font_family=style_data.get("font_family"),
            grid=style_data.get("grid"),
            legend_position=style_data.get("legend_position"),
            background=normalise_style_colour(style_data.get("background")),
            plot_background=normalise_style_colour(style_data.get("plot_background")),
            diagram_direction=style_data.get("diagram_direction"),
            highlights=style_data.get("highlights", {}) or {},
            labels=style_data.get("labels", {}) or {},
            orientation=style_data.get("orientation"),
        )
        data_roles = [
            DataRole(
                role=role_name,
                field=role_data.get("field"),
                transform=role_data.get("transform"),
                aggregation=role_data.get("aggregation"),
            )
            for role_name, role_data in (draft.roles or {}).items()
            if isinstance(role_data, dict)
        ]
        diagram_nodes = [
            DiagramNode(
                id=str(node["id"]),
                label=str(node["label"]),
                node_type=str(node.get("node_type", "process")),
            )
            for node in draft.diagram_nodes
            if isinstance(node, dict) and node.get("id") and node.get("label")
        ]
        diagram_edges = [
            DiagramEdge(
                source=str(edge["source"]),
                target=str(edge["target"]),
                label=edge.get("label"),
            )
            for edge in draft.diagram_edges
            if isinstance(edge, dict) and edge.get("source") and edge.get("target")
        ]
        notes: list[str] | None = None
        if draft.assumptions or draft.questions:
            notes = [f"Assumption: {item}" for item in draft.assumptions]
            notes.extend(f"Question: {item}" for item in draft.questions)
        return cls(
            visual_kind=draft.visual_kind,
            intent=draft.intent,
            chart_type=draft.chart_type,
            diagram_type=draft.diagram_type,
            data_roles=data_roles or None,
            filters=list(draft.filters) if draft.filters else None,
            grouping=list(draft.grouping) if draft.grouping else None,
            diagram_nodes=diagram_nodes or None,
            diagram_edges=diagram_edges or None,
            style=style,
            render_target=RenderTarget(renderer=draft.renderer),
            notes=notes,
        )
