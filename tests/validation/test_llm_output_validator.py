"""LLM output validator tests."""

from semantic_visual_builder.validation.llm_output_validator import LlmOutputValidator


def test_accepts_valid_chart_draft() -> None:
    result = LlmOutputValidator().validate_draft_json(
        {
            "visual_kind": "chart",
            "intent": "compare_categories",
            "chart_type": "bar",
            "roles": {},
            "renderer": "plotly",
            "confidence": 0.9,
        }
    )
    assert result.is_valid is True


def test_accepts_valid_flowchart_draft() -> None:
    result = LlmOutputValidator().validate_draft_json(
        {
            "visual_kind": "diagram",
            "intent": "show_process",
            "diagram_type": "flowchart",
            "roles": {},
            "renderer": "mermaid",
        }
    )
    assert result.is_valid is True


def test_rejects_python_renderer() -> None:
    result = LlmOutputValidator().validate_draft_json(
        {"visual_kind": "chart", "intent": "compare_categories", "chart_type": "bar", "roles": {}, "renderer": "python"}
    )
    assert result.is_valid is False


def test_rejects_graphviz_renderer() -> None:
    result = LlmOutputValidator().validate_draft_json(
        {"visual_kind": "diagram", "intent": "show_process", "diagram_type": "flowchart", "roles": {}, "renderer": "graphviz"}
    )
    assert result.is_valid is False


def test_rejects_unknown_chart_type() -> None:
    result = LlmOutputValidator().validate_draft_json(
        {"visual_kind": "chart", "intent": "compare_categories", "chart_type": "donut", "roles": {}}
    )
    assert result.is_valid is False


def test_rejects_invalid_confidence() -> None:
    result = LlmOutputValidator().validate_draft_json(
        {"visual_kind": "chart", "intent": "compare_categories", "chart_type": "bar", "roles": {}, "confidence": 2}
    )
    assert result.is_valid is False


def test_rejects_missing_required_fields() -> None:
    result = LlmOutputValidator().validate_draft_json({"intent": "compare_categories"})
    assert result.is_valid is False
