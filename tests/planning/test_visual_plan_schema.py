"""Visual plan schema tests."""

from semantic_visual_builder.planning.visual_plan_schema import DiagramEdge, DiagramNode, VisualPlan
from semantic_visual_builder.planning.visual_plan import summarize_visual_plan


def test_visual_plan_includes_diagram_counts_in_summary() -> None:
    plan = VisualPlan(
        visual_kind="diagram",
        intent="show_process",
        diagram_type="flowchart",
        diagram_nodes=[DiagramNode(id="A", label="Start"), DiagramNode(id="B", label="End")],
        diagram_edges=[DiagramEdge(source="A", target="B")],
    )
    summary = summarize_visual_plan(plan)
    assert "Diagram nodes: 2" in summary
    assert "Diagram edges: 1" in summary
