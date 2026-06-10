"""Visual plan helpers."""

from __future__ import annotations

from copy import deepcopy

from .visual_plan_schema import DataRole, VisualPlan


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
    for note in plan.notes:
        lines.append(f"Note: {note}")
    return "\n".join(lines)


def clone_visual_plan(plan: VisualPlan) -> VisualPlan:
    return deepcopy(plan)
