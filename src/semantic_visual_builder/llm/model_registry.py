"""Model registry helpers."""

from __future__ import annotations

from dataclasses import dataclass, field

from .ollama_client import OllamaModel


@dataclass
class ModelRegistry:
    """Track installed Ollama models and the selected model."""

    models: list[OllamaModel] = field(default_factory=list)
    selected_model: str | None = None

    def set_models(self, models: list[OllamaModel]) -> None:
        previous = self.selected_model
        self.models = list(models)
        names = self.get_model_names()
        if previous in names:
            self.selected_model = previous
        else:
            self.selected_model = names[0] if names else None

    def select_model(self, model_name: str) -> None:
        if model_name in self.get_model_names():
            self.selected_model = model_name

    def get_model_names(self) -> list[str]:
        return [model.name for model in self.models if model.name]
