"""Ollama generation tests."""

import base64
from types import SimpleNamespace

import pytest

from semantic_visual_builder.llm.ollama_client import (
    OllamaClient,
    OllamaGenerationError,
)


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
    assert captured["json"]["format"] == "json"
    assert captured["json"]["options"]["temperature"] == 0.0
    assert captured["json"]["options"]["num_predict"] == 256
    assert captured["json"]["keep_alive"] == "5m"
    assert captured["json"]["stream"] is False
    assert captured["timeout"] == client.generation_timeout_seconds


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


def test_generate_vision_sends_image_payload(tmp_path, monkeypatch: pytest.MonkeyPatch) -> None:
    captured = {}
    image_path = tmp_path / "sample.png"
    image_path.write_bytes(b"fake-image-bytes")

    def fake_post(url, json, timeout):
        captured["url"] = url
        captured["json"] = json
        captured["timeout"] = timeout
        return SimpleNamespace(
            raise_for_status=lambda: None,
            json=lambda: {"response": '{"ok":true}'},
        )

    monkeypatch.setattr("semantic_visual_builder.llm.ollama_client.requests.post", fake_post)
    client = OllamaClient(base_url="http://localhost:11434")
    response = client.generate_vision(
        model="gemma4:12b-it-qat",
        image_path=image_path,
        prompt="describe this image",
    )

    assert response == '{"ok":true}'
    assert captured["url"].endswith("/api/generate")
    assert captured["json"]["model"] == "gemma4:12b-it-qat"
    assert captured["json"]["prompt"] == "describe this image"
    assert captured["json"]["images"] == [
        base64.b64encode(b"fake-image-bytes").decode("ascii")
    ]
    assert captured["json"]["format"] == "json"
    assert captured["json"]["stream"] is False
    assert captured["timeout"] == client.generation_timeout_seconds
