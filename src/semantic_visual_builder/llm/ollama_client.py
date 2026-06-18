"""Ollama client for local model discovery."""

from __future__ import annotations

import base64
from dataclasses import dataclass
from pathlib import Path

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


class OllamaGenerationError(RuntimeError):
    """Raised when a controlled Ollama generation call fails."""


class OllamaClient:
    """Client for local Ollama discovery."""

    def __init__(
        self,
        base_url: str = "http://localhost:11434",
        timeout_seconds: float = 2.0,
        generation_timeout_seconds: float = 300.0,
    ):
        self.base_url = base_url.rstrip("/")
        self.timeout_seconds = timeout_seconds
        self.generation_timeout_seconds = generation_timeout_seconds

    def get_status(self) -> OllamaStatus:
        """Check whether Ollama is reachable."""

        try:
            response = requests.get(
                f"{self.base_url}/api/version", timeout=self.timeout_seconds
            )
            response.raise_for_status()
            payload = response.json()
            version = payload.get("version") if isinstance(payload, dict) else None
            return OllamaStatus(is_connected=True, version=version)
        except Exception as exc:
            return OllamaStatus(is_connected=False, error=str(exc))

    def list_models(self) -> list[OllamaModel]:
        """Return installed Ollama models, or an empty list if unavailable."""

        try:
            response = requests.get(
                f"{self.base_url}/api/tags", timeout=self.timeout_seconds
            )
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

    def chat(
        self,
        model: str,
        messages: list[dict[str, str]],
        system: str | None = None,
        temperature: float = 0.0,
        num_predict: int = 256,
        response_format: str = "json",
    ) -> str:
        """Run a multi-turn chat completion against Ollama.

        messages is a list of {"role": "user"|"assistant"|"system", "content": str}
        dicts. The assistant message content from the Ollama /api/chat response is
        returned. When response_format is "json" (the default for structured
        mapping), Ollama is asked to emit JSON.
        """
        if not model.strip():
            raise ValueError("model must not be blank")
        if not messages:
            raise ValueError("messages must not be empty")
        payload_messages: list[dict[str, str]] = []
        if system:
            payload_messages.append({"role": "system", "content": system})
        for message in messages:
            if (
                not isinstance(message, dict)
                or "role" not in message
                or "content" not in message
            ):
                raise ValueError("each message must have 'role' and 'content'")
            payload_messages.append(
                {"role": str(message["role"]), "content": str(message["content"])}
            )
        payload = {
            "model": model,
            "messages": payload_messages,
            "options": {
                "temperature": temperature,
                "num_predict": num_predict,
            },
            "stream": False,
            "keep_alive": "5m",
        }
        if response_format:
            payload["format"] = response_format
        try:
            response = requests.post(
                f"{self.base_url}/api/chat",
                json=payload,
                timeout=self.generation_timeout_seconds,
            )
            response.raise_for_status()
            data = response.json()
        except Exception as exc:
            raise OllamaGenerationError(str(exc)) from exc
        if not isinstance(data, dict) or "message" not in data:
            raise OllamaGenerationError("Unexpected Ollama chat response format.")
        message = data["message"]
        if not isinstance(message, dict) or not isinstance(message.get("content"), str):
            raise OllamaGenerationError("Unexpected Ollama chat response format.")
        return message["content"]

    def generate_vision(
        self,
        model: str,
        image_path: Path,
        prompt: str,
        system: str | None = None,
    ) -> str:
        if not model.strip():
            raise ValueError("model must not be blank")
        resolved_path = Path(image_path)
        if not resolved_path.is_file():
            raise ValueError(f"image_path does not exist: {resolved_path}")
        image_bytes = resolved_path.read_bytes()
        payload = {
            "model": model,
            "prompt": prompt,
            "system": system,
            "format": "json",
            "images": [base64.b64encode(image_bytes).decode("ascii")],
            "options": {
                "temperature": 0.0,
                "num_predict": 256,
            },
            "stream": False,
            "keep_alive": "5m",
        }
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=self.generation_timeout_seconds,
            )
            response.raise_for_status()
            data = response.json()
        except Exception as exc:
            raise OllamaGenerationError(str(exc)) from exc
        if (
            not isinstance(data, dict)
            or "response" not in data
            or not isinstance(data["response"], str)
        ):
            raise OllamaGenerationError("Unexpected Ollama response format.")
        return data["response"]

    def generate(
        self,
        model: str,
        prompt: str,
        system: str | None = None,
        temperature: float = 0.0,
    ) -> str:
        if not model.strip():
            raise ValueError("model must not be blank")
        payload = {
            "model": model,
            "prompt": prompt,
            "system": system,
            "format": "json",
            "options": {
                "temperature": temperature,
                "num_predict": 256,
            },
            "stream": False,
            "keep_alive": "5m",
        }
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=self.generation_timeout_seconds,
            )
            response.raise_for_status()
            data = response.json()
        except Exception as exc:
            raise OllamaGenerationError(str(exc)) from exc
        if (
            not isinstance(data, dict)
            or "response" not in data
            or not isinstance(data["response"], str)
        ):
            raise OllamaGenerationError("Unexpected Ollama response format.")
        return data["response"]
