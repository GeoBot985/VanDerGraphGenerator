"""Diagram plan builder tests."""

from semantic_visual_builder.planning.diagram_plan_builder import DiagramPlanBuilder
from semantic_visual_builder.validation.visual_plan_validator import VisualPlanValidator


def test_simple_process_text_creates_nodes() -> None:
    plan = DiagramPlanBuilder().build_basic_flowchart("A user submits a request. The analyst reviews it.")
    assert len(plan.diagram_nodes) == 2
    assert plan.diagram_nodes[0].label.startswith("A user submits")


def test_sequential_sentences_create_edges() -> None:
    plan = DiagramPlanBuilder().build_basic_flowchart("First step. Second step. Third step.")
    assert len(plan.diagram_edges) == 2


def test_complete_incomplete_creates_decision_and_branches() -> None:
    plan = DiagramPlanBuilder().build_basic_flowchart(
        "A user submits a request. The analyst reviews it. If complete, approve it. If incomplete, return it."
    )
    decision_nodes = [node for node in plan.diagram_nodes if node.node_type == "decision"]
    assert decision_nodes
    assert any(edge.label == "Yes" for edge in plan.diagram_edges)
    assert any(edge.label == "No" for edge in plan.diagram_edges)


def test_generated_plan_validates() -> None:
    plan = DiagramPlanBuilder().build_basic_flowchart("A user submits a request. The analyst reviews it.")
    result = VisualPlanValidator().validate(plan, None, None)
    assert result.is_valid is True
