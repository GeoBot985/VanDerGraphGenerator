"""Mermaid escaping tests."""

from semantic_visual_builder.planning.diagram_plan_builder import DiagramPlanBuilder
from semantic_visual_builder.planning.visual_plan_schema import DiagramEdge, DiagramNode, VisualPlan
from semantic_visual_builder.renderers.mermaid_renderer import MermaidRenderer
from semantic_visual_builder.validation.visual_plan_validator import VisualPlanValidator


def test_labels_with_quotes_and_newlines_are_sanitized() -> None:
    plan = VisualPlan(
        visual_kind="diagram",
        intent="show_process",
        diagram_type="flowchart",
        diagram_nodes=[DiagramNode(id="A", label='User "submits"\nrequest')],
        diagram_edges=[DiagramEdge(source="A", target="A")],
    )
    output = MermaidRenderer().render(plan)
    assert '"' not in output.content
    assert "\nrequest" not in output.content


def test_decision_nodes_use_diamond_syntax() -> None:
    plan = DiagramPlanBuilder().build_basic_flowchart("A user submits a request. If complete, approve it.")
    plan.diagram_nodes = [DiagramNode(id="A", label="Request complete?", node_type="decision"), DiagramNode(id="B", label="Approve")]
    plan.diagram_edges = [DiagramEdge(source="A", target="B", label="Yes")]
    output = MermaidRenderer().render(plan)
    assert "{Request complete?}" in output.content or "{Request complete}" in output.content


def test_edge_labels_render() -> None:
    plan = DiagramPlanBuilder().build_basic_flowchart("A user submits a request. If complete, approve it.")
    output = MermaidRenderer().render(plan)
    assert "|Yes|" in output.content or "|No|" in output.content


def test_unknown_edge_node_fails_validation() -> None:
    plan = VisualPlan(
        visual_kind="diagram",
        intent="show_process",
        diagram_type="flowchart",
        diagram_nodes=[DiagramNode(id="A", label="Start")],
        diagram_edges=[DiagramEdge(source="A", target="B")],
    )
    result = VisualPlanValidator().validate(plan, None, None)
    assert result.is_valid is False
