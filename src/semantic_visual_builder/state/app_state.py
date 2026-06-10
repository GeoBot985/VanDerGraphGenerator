"""Application state helpers."""

from __future__ import annotations

from dataclasses import dataclass, field

from semantic_visual_builder.data.dataset_context import DatasetContext
from semantic_visual_builder.knowledge.graph_matrix import GraphMatrix
from semantic_visual_builder.knowledge.product_kb import ProductKnowledgeBase
from semantic_visual_builder.planning.workflow_state import WorkflowState
from semantic_visual_builder.planning.visual_plan_schema import VisualPlan
from semantic_visual_builder.llm.model_registry import ModelRegistry
from semantic_visual_builder.llm.ollama_client import OllamaStatus
from semantic_visual_builder.state.conversation_state import ConversationState
from semantic_visual_builder.state.revision_history import RevisionHistory
from semantic_visual_builder.validation.validation_result import ValidationResult


@dataclass
class AppState:
    ollama_status: OllamaStatus | None = None
    model_registry: ModelRegistry = field(default_factory=ModelRegistry)
    dataset_context: DatasetContext = field(default_factory=DatasetContext)
    product_kb: ProductKnowledgeBase | None = None
    graph_matrix: GraphMatrix | None = None
    workflow_state: WorkflowState = field(default_factory=WorkflowState)
    conversation_state: ConversationState = field(default_factory=ConversationState)
    current_visual_plan: VisualPlan | None = None
    current_validation_result: ValidationResult | None = None
    revision_history: RevisionHistory = field(default_factory=RevisionHistory)
    status_messages: list[str] = field(default_factory=list)

    def add_status(self, message: str) -> None:
        self.status_messages.append(message)

    def set_visual_plan(self, plan: VisualPlan, description: str = "Updated visual plan") -> None:
        self.current_visual_plan = plan
        self.revision_history.add_revision(description, plan)

    def set_validation_result(self, result: ValidationResult) -> None:
        self.current_validation_result = result
