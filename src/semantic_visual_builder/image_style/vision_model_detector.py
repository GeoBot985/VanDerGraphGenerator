"""Heuristic detection of likely vision-capable Ollama models."""

from __future__ import annotations

_VISION_KEYWORDS = (
    "vision",
    "vl",
    "vlm",
    "llava",
    "moondream",
    "bakllava",
    "minicpm-v",
    "qwen2.5vl",
    "qwen-vl",
    "gemma3",
)


class VisionModelDetector:
    """Determine whether an Ollama model name suggests vision capability.

    This is a heuristic only. The model may still be used without vision if
    the user overrides, or fall back to deterministic extraction.
    """

    def is_likely_vision_model(self, model_name: str) -> bool:
        """Return True if model_name contains a known vision-capable keyword."""
        lowered = model_name.lower()
        return any(keyword in lowered for keyword in _VISION_KEYWORDS)

    def get_vision_capable_models(self, model_names: list[str]) -> list[str]:
        """Filter a list of model names to those that appear vision-capable."""
        return [name for name in model_names if self.is_likely_vision_model(name)]
