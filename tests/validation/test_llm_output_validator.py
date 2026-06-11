"""LLM output validator tests."""

from semantic_visual_builder.knowledge.graph_matrix import GraphMatrixLoader
from semantic_visual_builder.utils.paths import get_graph_matrix_dir
from semantic_visual_builder.validation.llm_output_validator import LlmOutputValidator


def _matrix():
    return GraphMatrixLoader(get_graph_matrix_dir() / "graph_matrix.json").load()


def test_accepts_valid_chart_draft() -> None:
    result = LlmOutputValidator().validate_draft_json(
        {
            "action": "create_plan",
            "visual_kind": "chart",
            "intent": "compare_categories",
            "chart_type": "bar",
            "roles": {"category": {}, "measure": {}},
            "renderer": "plotly",
            "confidence": 0.9,
        },
        _matrix(),
    )
    assert result.is_valid is True


def test_accepts_valid_flowchart_draft() -> None:
    result = LlmOutputValidator().validate_draft_json(
        {
            "action": "create_plan",
            "visual_kind": "diagram",
            "intent": "show_process",
            "diagram_type": "flowchart",
            "roles": {"nodes": {}, "edges": {}},
            "diagram_nodes": [
                {"id": "A", "label": "User"},
                {"id": "B", "label": "App"},
            ],
            "diagram_edges": [{"source": "A", "target": "B"}],
            "renderer": "mermaid",
        },
        _matrix(),
    )
    assert result.is_valid is True


def test_accepts_valid_sequence_diagram_draft() -> None:
    result = LlmOutputValidator().validate_draft_json(
        {
            "action": "create_plan",
            "visual_kind": "diagram",
            "intent": "show_process",
            "diagram_type": "sequence_diagram",
            "roles": {"nodes": {}, "edges": {}},
            "diagram_nodes": [
                {"id": "A", "label": "User"},
                {"id": "B", "label": "App"},
            ],
            "diagram_edges": [{"source": "A", "target": "B", "label": "Request"}],
            "renderer": "mermaid",
        },
        _matrix(),
    )
    assert result.is_valid is True


def test_rejects_python_renderer() -> None:
    result = LlmOutputValidator().validate_draft_json(
        {
            "action": "create_plan",
            "visual_kind": "chart",
            "intent": "compare_categories",
            "chart_type": "bar",
            "roles": {"category": {}, "measure": {}},
            "renderer": "python",
        },
        _matrix(),
    )
    assert result.is_valid is False


def test_rejects_graphviz_renderer() -> None:
    result = LlmOutputValidator().validate_draft_json(
        {
            "action": "create_plan",
            "visual_kind": "diagram",
            "intent": "show_process",
            "diagram_type": "flowchart",
            "roles": {"nodes": {}, "edges": {}},
            "diagram_nodes": [
                {"id": "A", "label": "User"},
                {"id": "B", "label": "App"},
            ],
            "diagram_edges": [{"source": "A", "target": "B"}],
            "renderer": "graphviz",
        },
        _matrix(),
    )
    assert result.is_valid is False


def test_rejects_unknown_chart_type() -> None:
    result = LlmOutputValidator().validate_draft_json(
        {
            "action": "create_plan",
            "visual_kind": "chart",
            "intent": "compare_categories",
            "chart_type": "donut",
            "roles": {"category": {}, "measure": {}},
        },
        _matrix(),
    )
    assert result.is_valid is False


def test_rejects_invalid_confidence() -> None:
    result = LlmOutputValidator().validate_draft_json(
        {
            "action": "create_plan",
            "visual_kind": "chart",
            "intent": "compare_categories",
            "chart_type": "bar",
            "roles": {"category": {}, "measure": {}},
            "confidence": 2,
        },
        _matrix(),
    )
    assert result.is_valid is False


def test_rejects_missing_required_fields() -> None:
    result = LlmOutputValidator().validate_draft_json(
        {"intent": "compare_categories"},
        _matrix(),
    )
    assert result.is_valid is False
