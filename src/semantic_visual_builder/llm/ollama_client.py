"""Ollama client placeholder for local model discovery and generation."""

from dataclasses import dataclass


@dataclass(frozen=True)
class OllamaModel:
    """Represents an installed Ollama model."""

    name: str
    size: int | None = None


class OllamaClient:
    """Stub client for future Ollama integration."""

    def list_models(self) -> list[OllamaModel]:
        """Return installed Ollama models.

        Sprint 0 stub: returns an empty list.
        """
        return []
