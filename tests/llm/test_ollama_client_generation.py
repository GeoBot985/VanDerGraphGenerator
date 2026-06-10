"""Ollama generation tests."""

from types import SimpleNamespace

import pytest

from semantic_visual_builder.llm.ollama_client import OllamaClient, OllamaGenerationError


def test_generate_sends_model_prompt_and_default_temperature(monkeypatch: pytest.MonkeyPatch) -> None:
    captured = {}

    def fake_post(url, json, timeout):
        captured["url"] = url
        captured["json"] = json
        captured["timeout"] = timeout
        return SimpleNamespace(
            raise_for_status=lambda: None,
            json=lambda: {"response": "hello"},
        )

    monkeypatch.setattr("semantic_visual_builder.llm.ollama_client.requests.post", fake_post)
    client = OllamaClient(base_url="http://localhost:11434", timeout_seconds=3.0)
    response = client.generate(model="gemma4:12b", prompt="prompt text")
    assert response == "hello"
    assert captured["url"].endswith("/api/generate")
    assert captured["json"]["model"] == "gemma4:12b"
    assert captured["json"]["prompt"] == "prompt text"
    assert captured["json"]["temperature"] == 0.0
    assert captured["json"]["stream"] is False


def test_generate_raises_on_connection_failure(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_post(url, json, timeout):
        raise OSError("offline")

    monkeypatch.setattr("semantic_visual_builder.llm.ollama_client.requests.post", fake_post)
    client = OllamaClient()
    with pytest.raises(OllamaGenerationError):
        client.generate(model="gemma4:12b", prompt="prompt text")


def test_generate_raises_on_malformed_response(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_post(url, json, timeout):
        return SimpleNamespace(
            raise_for_status=lambda: None,
            json=lambda: {"unexpected": "payload"},
        )

    monkeypatch.setattr("semantic_visual_builder.llm.ollama_client.requests.post", fake_post)
    client = OllamaClient()
    with pytest.raises(OllamaGenerationError):
        client.generate(model="gemma4:12b", prompt="prompt text")
