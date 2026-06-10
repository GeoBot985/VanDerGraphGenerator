"""Ollama stub tests."""

from semantic_visual_builder.llm.ollama_client import OllamaClient


def test_list_models_returns_empty_list() -> None:
    assert OllamaClient().list_models() == []
