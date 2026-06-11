"""Mermaid renderer tests."""

from semantic_visual_builder.planning.diagram_plan_builder import DiagramPlanBuilder
from semantic_visual_builder.planning.visual_plan_schema import DiagramEdge, DiagramNode
from semantic_visual_builder.renderers.mermaid_renderer import MermaidRenderer
from semantic_visual_builder.renderers.renderer_result import RendererOutput


def test_can_render_returns_true_for_flowchart() -> None:
    plan = DiagramPlanBuilder().build_basic_flowchart(
        "A user submits a request. An analyst reviews it."
    )
    assert MermaidRenderer().can_render(plan) is True


def test_can_render_returns_true_for_sequence_diagram() -> None:
    plan = DiagramPlanBuilder().build_basic_flowchart(
        "A user submits a request. An analyst reviews it."
    )
    plan.diagram_type = "sequence_diagram"
    assert MermaidRenderer().can_render(plan) is True


def test_mermaid_output_starts_with_flowchart_td() -> None:
    plan = DiagramPlanBuilder().build_basic_flowchart(
        "A user submits a request. An analyst reviews it."
    )
    output = MermaidRenderer().render(plan)
    assert output.output_type == "mermaid"
    assert output.content.startswith("flowchart TD")


def test_sequence_diagram_output_starts_with_sequence_diagram() -> None:
    plan = DiagramPlanBuilder().build_basic_flowchart(
        "A user submits a request. An analyst reviews it."
    )
    plan.diagram_type = "sequence_diagram"
    output = MermaidRenderer().render(plan)
    assert output.output_type == "mermaid"
    assert output.content.startswith("sequenceDiagram")


def test_mermaid_output_includes_nodes_and_edges() -> None:
    plan = DiagramPlanBuilder().build_basic_flowchart(
        "A user submits a request. An analyst reviews it."
    )
    output = MermaidRenderer().render(plan)
    assert "A[" in output.content
    assert "-->" in output.content


def test_validate_output_catches_blank_output() -> None:
    result = MermaidRenderer().validate_output(
        RendererOutput(renderer_name="mermaid", output_type="mermaid", content="")
    )
    assert result.is_valid is False


def test_erd_output_starts_with_erd_diagram() -> None:
    plan = DiagramPlanBuilder().build_basic_flowchart("A user submits a request.")
    plan.diagram_type = "erd"
    plan.diagram_nodes = [
        DiagramNode(id="Customer", label="Customer", node_type="entity"),
        DiagramNode(id="Order", label="Order", node_type="entity"),
    ]
    plan.diagram_edges = [DiagramEdge(source="Customer", target="Order", label="places")]
    output = MermaidRenderer().render(plan)
    assert output.content.startswith("erDiagram")


def test_timeline_output_starts_with_timeline() -> None:
    plan = DiagramPlanBuilder().build_basic_flowchart("A user submits a request.")
    plan.diagram_type = "timeline"
    plan.diagram_nodes = [
        DiagramNode(id="2026-Q1", label="Project kickoff", node_type="event"),
        DiagramNode(id="2026-Q2", label="Launch", node_type="event"),
    ]
    output = MermaidRenderer().render(plan)
    assert output.content.startswith("timeline")
