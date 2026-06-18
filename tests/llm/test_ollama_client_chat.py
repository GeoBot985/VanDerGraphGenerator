"""Ollama chat completion tests."""

from types import SimpleNamespace

import pytest

from semantic_visual_builder.llm.ollama_client import (
    OllamaClient,
    OllamaGenerationError,
)


def test_chat_sends_messages_payload(monkeypatch: pytest.MonkeyPatch) -> None:
    captured = {}

    def fake_post(url, json, timeout):
        captured["url"] = url
        captured["json"] = json
        captured["timeout"] = timeout
        return SimpleNamespace(
            raise_for_status=lambda: None,
            json=lambda: {"message": {"role": "assistant", "content": "hello"}},
        )

    monkeypatch.setattr("semantic_visual_builder.llm.ollama_client.requests.post", fake_post)
    client = OllamaClient(base_url="http://localhost:11434")
    response = client.chat(
        model="gemma4:12b",
        messages=[{"role": "user", "content": "hi"}],
        system="be strict",
    )
    assert response == "hello"
    assert captured["url"].endswith("/api/chat")
    assert captured["json"]["model"] == "gemma4:12b"
    assert captured["json"]["messages"][0] == {"role": "system", "content": "be strict"}
    assert captured["json"]["messages"][1] == {"role": "user", "content": "hi"}
    assert captured["json"]["format"] == "json"
    assert captured["json"]["stream"] is False
    assert captured["json"]["options"]["temperature"] == 0.0
    assert captured["json"]["keep_alive"] == "5m"
    assert captured["timeout"] == client.generation_timeout_seconds


def test_chat_without_system_omits_system_message(monkeypatch: pytest.MonkeyPatch) -> None:
    captured = {}

    def fake_post(url, json, timeout):
        captured["json"] = json
        return SimpleNamespace(
            raise_for_status=lambda: None,
            json=lambda: {"message": {"role": "assistant", "content": "ok"}},
        )

    monkeypatch.setattr("semantic_visual_builder.llm.ollama_client.requests.post", fake_post)
    OllamaClient().chat(model="m", messages=[{"role": "user", "content": "hi"}])
    assert captured["json"]["messages"] == [{"role": "user", "content": "hi"}]


def test_chat_raises_on_blank_model() -> None:
    with pytest.raises(ValueError):
        OllamaClient().chat(model="  ", messages=[{"role": "user", "content": "hi"}])


def test_chat_raises_on_empty_messages() -> None:
    with pytest.raises(ValueError):
        OllamaClient().chat(model="m", messages=[])


def test_chat_raises_on_connection_failure(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_post(url, json, timeout):
        raise OSError("offline")

    monkeypatch.setattr("semantic_visual_builder.llm.ollama_client.requests.post", fake_post)
    with pytest.raises(OllamaGenerationError):
        OllamaClient().chat(model="m", messages=[{"role": "user", "content": "hi"}])


def test_chat_raises_on_malformed_response(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_post(url, json, timeout):
        return SimpleNamespace(
            raise_for_status=lambda: None,
            json=lambda: {"unexpected": "payload"},
        )

    monkeypatch.setattr("semantic_visual_builder.llm.ollama_client.requests.post", fake_post)
    with pytest.raises(OllamaGenerationError):
        OllamaClient().chat(model="m", messages=[{"role": "user", "content": "hi"}])


def test_chat_can_disable_json_format(monkeypatch: pytest.MonkeyPatch) -> None:
    captured = {}

    def fake_post(url, json, timeout):
        captured["json"] = json
        return SimpleNamespace(
            raise_for_status=lambda: None,
            json=lambda: {"message": {"role": "assistant", "content": "ok"}},
        )

    monkeypatch.setattr("semantic_visual_builder.llm.ollama_client.requests.post", fake_post)
    OllamaClient().chat(
        model="m",
        messages=[{"role": "user", "content": "hi"}],
        response_format="",
    )
    assert "format" not in captured["json"]
