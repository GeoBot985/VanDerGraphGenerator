"""JSON repair prompt tests."""

from semantic_visual_builder.llm.json_repair import JsonRepair


def test_repair_prompt_includes_invalid_response_and_error() -> None:
    prompt = JsonRepair().build_repair_prompt("bad response", "parse error")
    assert "bad response" in prompt
    assert "parse error" in prompt
    assert "Return one valid JSON object only." in prompt
