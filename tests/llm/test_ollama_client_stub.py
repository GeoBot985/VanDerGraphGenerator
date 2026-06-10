"""Ollama client tests."""

from types import SimpleNamespace

import pytest

from semantic_visual_builder.llm.ollama_client import OllamaClient


def test_get_status_connected(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_get(url, timeout):
        return SimpleNamespace(
            raise_for_status=lambda: None,
            json=lambda: {"version": "0.1.0"},
        )

    monkeypatch.setattr("semantic_visual_builder.llm.ollama_client.requests.get", fake_get)
    status = OllamaClient().get_status()
    assert status.is_connected is True
    assert status.version == "0.1.0"


def test_get_status_handles_failure(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_get(url, timeout):
        raise OSError("offline")

    monkeypatch.setattr("semantic_visual_builder.llm.ollama_client.requests.get", fake_get)
    status = OllamaClient().get_status()
    assert status.is_connected is False
    assert "offline" in status.error


def test_list_models_parses_models(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_get(url, timeout):
        return SimpleNamespace(
            raise_for_status=lambda: None,
            json=lambda: {"models": [{"name": "llama3:latest", "size": 123}]},
        )

    monkeypatch.setattr("semantic_visual_builder.llm.ollama_client.requests.get", fake_get)
    models = OllamaClient().list_models()
    assert [model.name for model in models] == ["llama3:latest"]


def test_list_models_returns_empty_list_on_failure(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_get(url, timeout):
        raise OSError("offline")

    monkeypatch.setattr("semantic_visual_builder.llm.ollama_client.requests.get", fake_get)
    assert OllamaClient().list_models() == []
