"""LLM response parser tests."""

import pytest

from semantic_visual_builder.llm.llm_response_parser import LlmResponseParser


def test_parses_raw_json() -> None:
    data = LlmResponseParser().parse_json_response('{"visual_kind":"chart","intent":"x","roles":{}}')
    assert data["visual_kind"] == "chart"


def test_parses_fenced_json() -> None:
    data = LlmResponseParser().parse_json_response("```json\n{\"visual_kind\":\"diagram\",\"intent\":\"x\",\"roles\":{}}\n```")
    assert data["visual_kind"] == "diagram"


def test_rejects_prose() -> None:
    with pytest.raises(ValueError, match="LLM response is not valid JSON"):
        LlmResponseParser().parse_json_response("This is not JSON.")


def test_rejects_multiple_json_objects() -> None:
    with pytest.raises(ValueError):
        LlmResponseParser().parse_json_response('{"a":1}{"b":2}')


def test_raises_clear_error() -> None:
    with pytest.raises(ValueError):
        LlmResponseParser().parse_json_response("```json\nnot-json\n```")
