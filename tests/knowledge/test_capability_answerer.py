"""Capability answerer tests."""

from semantic_visual_builder.knowledge.capability_answerer import CapabilityAnswerer
from semantic_visual_builder.knowledge.product_kb import ProductKnowledgeLoader
from semantic_visual_builder.utils.paths import get_kb_dir


def _answerer() -> CapabilityAnswerer:
    return CapabilityAnswerer(ProductKnowledgeLoader(get_kb_dir()).load())


def test_answers_supported_chart_question() -> None:
    answer = _answerer().answer("What chart types are supported?")
    assert "bar" in answer and "line" in answer


def test_answers_supported_flowchart_question() -> None:
    answer = _answerer().answer("Can you do flowcharts?")
    assert "flowcharts are supported" in answer.lower()


def test_generated_python_is_future_only() -> None:
    answer = _answerer().answer("Can you do generated Python graphs?")
    assert "future renderer plugin" in answer


def test_graphviz_is_not_mvp() -> None:
    answer = _answerer().answer("Do you support Graphviz?")
    assert "not part of the MVP" in answer or "not supported in the MVP" in answer


def test_unknown_support_is_not_hallucinated() -> None:
    answer = _answerer().answer("Can you do underwater volcano charts?")
    assert "does not list" in answer.lower()
