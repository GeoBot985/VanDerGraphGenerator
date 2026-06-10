"""Ollama client for local model discovery."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import requests


@dataclass(frozen=True)
class OllamaModel:
    """Represents an installed Ollama model."""

    name: str
    model: str | None = None
    size: int | None = None
    modified_at: str | None = None
    parameter_size: str | None = None
    quantization_level: str | None = None


@dataclass(frozen=True)
class OllamaStatus:
    """Current Ollama connectivity state."""

    is_connected: bool
    version: str | None = None
    error: str | None = None


class OllamaClient:
    """Client for local Ollama discovery."""

    def __init__(self, base_url: str = "http://localhost:11434", timeout_seconds: float = 2.0):
        self.base_url = base_url.rstrip("/")
        self.timeout_seconds = timeout_seconds

    def get_status(self) -> OllamaStatus:
        """Check whether Ollama is reachable."""

        try:
            response = requests.get(f"{self.base_url}/api/version", timeout=self.timeout_seconds)
            response.raise_for_status()
            payload = response.json()
            version = payload.get("version") if isinstance(payload, dict) else None
            return OllamaStatus(is_connected=True, version=version)
        except Exception as exc:
            return OllamaStatus(is_connected=False, error=str(exc))

    def list_models(self) -> list[OllamaModel]:
        """Return installed Ollama models, or an empty list if unavailable."""

        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=self.timeout_seconds)
            response.raise_for_status()
            payload = response.json()
        except Exception:
            return []
        models: list[OllamaModel] = []
        for item in payload.get("models", []) if isinstance(payload, dict) else []:
            if not isinstance(item, dict):
                continue
            models.append(
                OllamaModel(
                    name=str(item.get("name", "")),
                    model=item.get("model"),
                    size=item.get("size"),
                    modified_at=item.get("modified_at"),
                    parameter_size=item.get("parameter_size"),
                    quantization_level=item.get("quantization_level"),
                )
            )
        return models

    def chat(self, model: str, messages: list[dict[str, str]]) -> str:
        raise NotImplementedError("Chat generation is planned for a later sprint.")
