"""Visual plan helpers."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import asdict
from typing import Any

from semantic_visual_builder.llm.llm_mapping_result import LlmVisualPlanDraft

from .visual_plan_schema import DataRole, DiagramEdge, DiagramNode, RenderTarget, StyleIntent, VisualPlan


def normalise_style_colour(value: object) -> str | None:
    if value is None:
        return None
    if isinstance(value, str):
        return value
    if isinstance(value, dict):
        colour = value.get("color") or value.get("colour") or value.get("value")
        if isinstance(colour, str):
            return colour
    return str(value)


def get_role(plan: VisualPlan, role: str) -> DataRole | None:
    for item in plan.data_roles:
        if item.role == role:
            return item
    return None


def set_role(
    plan: VisualPlan,
    role: str,
    field: str | None,
    transform: str | None = None,
    aggregation: str | None = None,
) -> None:
    existing = get_role(plan, role)
    if existing is not None:
        existing.field = field
        existing.transform = transform
        existing.aggregation = aggregation
        return
    plan.data_roles.append(
        DataRole(role=role, field=field, transform=transform, aggregation=aggregation)
    )


def summarize_visual_plan(plan: VisualPlan) -> str:
    lines = [f"Visual kind: {plan.visual_kind}", f"Intent: {plan.intent}"]
    if plan.chart_type:
        lines.append(f"Chart type: {plan.chart_type}")
    if plan.diagram_type:
        lines.append(f"Diagram type: {plan.diagram_type}")
    if plan.diagram_nodes:
        lines.append(f"Diagram nodes: {len(plan.diagram_nodes)}")
    if plan.diagram_edges:
        lines.append(f"Diagram edges: {len(plan.diagram_edges)}")
    for role in plan.data_roles:
        descriptor = role.field or "unassigned"
        if role.transform:
            descriptor += f" grouped by {role.transform}"
        if role.aggregation:
            descriptor += f" aggregation {role.aggregation}"
        lines.append(f"{role.role.upper()}: {descriptor}")
    if plan.render_target.renderer:
        lines.append(f"Renderer target: {plan.render_target.renderer}")
    if plan.style.title:
        lines.append(f"Title: {plan.style.title}")
    if plan.style.subtitle:
        lines.append(f"Subtitle: {plan.style.subtitle}")
    if plan.style.colour_scheme:
        lines.append(f"Colour scheme: {plan.style.colour_scheme}")
    if isinstance(plan.style.palette, dict) and plan.style.palette.get("primary"):
        lines.append(f"Primary colour: {plan.style.palette.get('primary')}")
    if plan.style.background:
        lines.append(f"Background: {plan.style.background}")
    if plan.style.plot_background:
        lines.append(f"Plot background: {plan.style.plot_background}")
    if plan.style.orientation:
        lines.append(f"Orientation: {plan.style.orientation}")
    if plan.style.highlights:
        lines.append(f"Highlights: {plan.style.highlights}")
    if plan.metadata.plan_id:
        lines.append(f"Plan ID: {plan.metadata.plan_id}")
    if plan.metadata.mapping_method:
        lines.append(f"Mapping method: {plan.metadata.mapping_method}")
    lines.append(f"Preview stale: {'yes' if plan.metadata.is_preview_stale else 'no'}")
    for note in plan.notes:
        lines.append(f"Note: {note}")
    return "\n".join(lines)


def clone_visual_plan(plan: VisualPlan) -> VisualPlan:
    return deepcopy(plan)


def visual_plan_from_llm_draft(draft: LlmVisualPlanDraft) -> VisualPlan:
    plan = VisualPlan(
        visual_kind=draft.visual_kind,
        intent=draft.intent,
        chart_type=draft.chart_type,
        diagram_type=draft.diagram_type,
        style=StyleIntent(
            title=(draft.style or {}).get("title"),
            subtitle=(draft.style or {}).get("subtitle"),
            colour_scheme=(draft.style or {}).get("colour_scheme"),
            palette=(draft.style or {}).get("palette", {}) or {},
            font_family=(draft.style or {}).get("font_family"),
            grid=(draft.style or {}).get("grid"),
            legend_position=(draft.style or {}).get("legend_position"),
            background=normalise_style_colour((draft.style or {}).get("background")),
            plot_background=normalise_style_colour(
                (draft.style or {}).get("plot_background")
            ),
            diagram_direction=(draft.style or {}).get("diagram_direction"),
            highlights=(draft.style or {}).get("highlights", {}) or {},
            labels=(draft.style or {}).get("labels", {}) or {},
            orientation=(draft.style or {}).get("orientation"),
        ),
        render_target=RenderTarget(renderer=draft.renderer),
    )
    for role_name, role_data in (draft.roles or {}).items():
        if not isinstance(role_data, dict):
            continue
        plan.data_roles.append(
            DataRole(
                role=role_name,
                field=role_data.get("field"),
                transform=role_data.get("transform"),
                aggregation=role_data.get("aggregation"),
            )
        )
    plan.filters = [item for item in draft.filters if isinstance(item, dict)]
    plan.grouping = [item for item in draft.grouping if isinstance(item, str)]
    for node_data in getattr(draft, "diagram_nodes", []) or []:
        if isinstance(node_data, dict) and node_data.get("id") and node_data.get("label"):
            plan.diagram_nodes.append(
                DiagramNode(
                    id=str(node_data["id"]),
                    label=str(node_data["label"]),
                    node_type=str(node_data.get("node_type", "process")),
                )
            )
    for edge_data in getattr(draft, "diagram_edges", []) or []:
        if isinstance(edge_data, dict) and edge_data.get("source") and edge_data.get("target"):
            plan.diagram_edges.append(
                DiagramEdge(
                    source=str(edge_data["source"]),
                    target=str(edge_data["target"]),
                    label=edge_data.get("label"),
                )
            )
    plan.notes.extend([f"Assumption: {item}" for item in draft.assumptions])
    if draft.questions:
        plan.notes.extend([f"Question: {item}" for item in draft.questions])
    plan.metadata.assumptions = list(draft.assumptions)
    plan.metadata.pending_questions = list(draft.questions)
    plan.metadata.confidence = draft.confidence
    plan.metadata.created_from = "llm"
    return plan


def visual_plan_to_dict(plan: VisualPlan) -> dict[str, Any]:
    return asdict(plan)


def visual_plan_from_dict(data: dict[str, Any]) -> VisualPlan:
    plan = VisualPlan(
        visual_kind=str(data.get("visual_kind", "chart")),
        intent=str(data.get("intent", "unknown")),
        chart_type=data.get("chart_type"),
        diagram_type=data.get("diagram_type"),
    )
    for role_data in data.get("data_roles", []) or []:
        if isinstance(role_data, dict):
            plan.data_roles.append(
                DataRole(
                    role=str(role_data.get("role", "")),
                    field=role_data.get("field"),
                    transform=role_data.get("transform"),
                    aggregation=role_data.get("aggregation"),
                )
            )
    for item in data.get("filters", []) or []:
        if isinstance(item, dict):
            plan.filters.append(item)
    for item in data.get("grouping", []) or []:
        if isinstance(item, str):
            plan.grouping.append(item)
    for node_data in data.get("diagram_nodes", []) or []:
        if isinstance(node_data, dict) and node_data.get("id") and node_data.get("label"):
            plan.diagram_nodes.append(
                DiagramNode(
                    id=str(node_data["id"]),
                    label=str(node_data["label"]),
                    node_type=str(node_data.get("node_type", "process")),
                )
            )
    for edge_data in data.get("diagram_edges", []) or []:
        if isinstance(edge_data, dict) and edge_data.get("source") and edge_data.get("target"):
            plan.diagram_edges.append(
                DiagramEdge(
                    source=str(edge_data["source"]),
                    target=str(edge_data["target"]),
                    label=edge_data.get("label"),
                )
            )
    style_data = data.get("style", {})
    if isinstance(style_data, dict):
        plan.style = StyleIntent(
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
    render_target_data = data.get("render_target", {})
    if isinstance(render_target_data, dict):
        plan.render_target = RenderTarget(
            renderer=render_target_data.get("renderer"),
            output_format=render_target_data.get("output_format"),
        )
    metadata_data = data.get("metadata", {})
    if isinstance(metadata_data, dict):
        plan.metadata.plan_id = metadata_data.get("plan_id")
        plan.metadata.created_from = metadata_data.get("created_from")
        plan.metadata.mapping_method = metadata_data.get("mapping_method")
        plan.metadata.confidence = metadata_data.get("confidence")
        plan.metadata.assumptions = list(metadata_data.get("assumptions", [])) if isinstance(metadata_data.get("assumptions"), list) else []
        plan.metadata.pending_questions = list(metadata_data.get("pending_questions", [])) if isinstance(metadata_data.get("pending_questions"), list) else []
        plan.metadata.is_preview_stale = bool(metadata_data.get("is_preview_stale", True))
    return plan


def merge_visual_plans(base: VisualPlan, update: VisualPlan) -> VisualPlan:
    merged = clone_visual_plan(base)
    merged.visual_kind = update.visual_kind or merged.visual_kind
    merged.intent = update.intent or merged.intent
    merged.chart_type = update.chart_type or merged.chart_type
    merged.diagram_type = update.diagram_type or merged.diagram_type
    merged.render_target.renderer = update.render_target.renderer or merged.render_target.renderer
    merged.render_target.output_format = update.render_target.output_format or merged.render_target.output_format

    if update.data_roles:
        for role in update.data_roles:
            set_role(merged, role.role, role.field, role.transform, role.aggregation)

    if update.filters:
        merged.filters = [deepcopy(item) for item in update.filters]
    if update.grouping:
        merged.grouping = list(update.grouping)
    if update.diagram_nodes:
        merged.diagram_nodes = deepcopy(update.diagram_nodes)
    if update.diagram_edges:
        merged.diagram_edges = deepcopy(update.diagram_edges)

    if update.style.title is not None:
        merged.style.title = update.style.title
    if update.style.subtitle is not None:
        merged.style.subtitle = update.style.subtitle
    if update.style.colour_scheme is not None:
        merged.style.colour_scheme = update.style.colour_scheme
    if update.style.palette:
        merged.style.palette = deepcopy(update.style.palette)
    if update.style.font_family is not None:
        merged.style.font_family = update.style.font_family
    if update.style.grid is not None:
        merged.style.grid = update.style.grid
    if update.style.legend_position is not None:
        merged.style.legend_position = update.style.legend_position
    if update.style.background is not None:
        merged.style.background = update.style.background
    if update.style.plot_background is not None:
        merged.style.plot_background = update.style.plot_background
    if update.style.diagram_direction is not None:
        merged.style.diagram_direction = update.style.diagram_direction
    if update.style.highlights:
        merged.style.highlights = deepcopy(update.style.highlights)
    if update.style.labels:
        merged.style.labels = deepcopy(update.style.labels)
    if update.style.orientation is not None:
        merged.style.orientation = update.style.orientation

    if update.metadata.plan_id is not None:
        merged.metadata.plan_id = update.metadata.plan_id
    if update.metadata.created_from is not None:
        merged.metadata.created_from = update.metadata.created_from
    if update.metadata.mapping_method is not None:
        merged.metadata.mapping_method = update.metadata.mapping_method
    if update.metadata.confidence is not None:
        merged.metadata.confidence = update.metadata.confidence
    if update.metadata.assumptions:
        merged.metadata.assumptions = list(update.metadata.assumptions)
    if update.metadata.pending_questions:
        merged.metadata.pending_questions = list(update.metadata.pending_questions)
    merged.metadata.is_preview_stale = update.metadata.is_preview_stale if update.metadata.is_preview_stale is not None else merged.metadata.is_preview_stale

    if update.notes:
        merged.notes.extend(item for item in update.notes if item not in merged.notes)
    return merged
