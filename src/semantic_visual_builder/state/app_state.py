"""Application state helpers."""

from __future__ import annotations

from dataclasses import dataclass, field

from semantic_visual_builder.data.dataset_context import DatasetContext
from semantic_visual_builder.knowledge.graph_matrix import GraphMatrix
from semantic_visual_builder.knowledge.product_kb import ProductKnowledgeBase
from semantic_visual_builder.llm.model_registry import ModelRegistry
from semantic_visual_builder.llm.ollama_client import OllamaStatus


@dataclass
class AppState:
    ollama_status: OllamaStatus | None = None
    model_registry: ModelRegistry = field(default_factory=ModelRegistry)
    dataset_context: DatasetContext = field(default_factory=DatasetContext)
    product_kb: ProductKnowledgeBase | None = None
    graph_matrix: GraphMatrix | None = None
    status_messages: list[str] = field(default_factory=list)

    def add_status(self, message: str) -> None:
        self.status_messages.append(message)
