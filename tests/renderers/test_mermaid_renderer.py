"""Mermaid renderer tests."""

from semantic_visual_builder.planning.diagram_plan_builder import DiagramPlanBuilder
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
