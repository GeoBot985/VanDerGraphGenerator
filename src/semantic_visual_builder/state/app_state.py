"""Application state helpers."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from semantic_visual_builder.data.dataset_context import DatasetContext
from semantic_visual_builder.knowledge.graph_matrix import GraphMatrix
from semantic_visual_builder.knowledge.product_kb import ProductKnowledgeBase
from semantic_visual_builder.planning.workflow_state import WorkflowState
from semantic_visual_builder.planning.visual_plan_schema import VisualPlan
from semantic_visual_builder.llm.model_registry import ModelRegistry
from semantic_visual_builder.llm.llm_mapping_result import LlmMappingResult
from semantic_visual_builder.llm.ollama_client import OllamaStatus
from semantic_visual_builder.planning.clarification import PendingClarification
from semantic_visual_builder.state.conversation_state import ConversationState
from semantic_visual_builder.state.revision_history import RevisionHistory
from semantic_visual_builder.renderers.renderer_result import RendererOutput
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
    last_renderer_output: RendererOutput | None = None
    last_preview_path: Path | None = None
    llm_mapping_enabled: bool = True
    last_llm_mapping_result: LlmMappingResult | None = None
    last_mapping_method: str | None = None
    last_fallback_reason: str | None = None
    pending_clarification: PendingClarification | None = None
    active_recipe_path: Path | None = None
    active_recipe_name: str | None = None
    status_messages: list[str] = field(default_factory=list)

    def add_status(self, message: str) -> None:
        self.status_messages.append(message)

    def set_visual_plan(self, plan: VisualPlan, description: str = "Updated visual plan") -> None:
        self.current_visual_plan = plan
        self.pending_clarification = None
        self.mark_preview_stale()
        self.revision_history.add_revision(
            description,
            plan,
            mapping_method=plan.metadata.mapping_method,
            preview_stale=True,
        )
        self.add_status("Visual plan changed. Preview needs regeneration.")

    def set_validation_result(self, result: ValidationResult) -> None:
        self.current_validation_result = result

    def set_renderer_output(self, output: RendererOutput) -> None:
        self.last_renderer_output = output
        if self.current_visual_plan is not None:
            self.current_visual_plan.metadata.is_preview_stale = False

    def set_preview_path(self, path: Path) -> None:
        self.last_preview_path = path
        if self.current_visual_plan is not None:
            self.current_visual_plan.metadata.is_preview_stale = False

    def set_llm_mapping_enabled(self, enabled: bool) -> None:
        self.llm_mapping_enabled = enabled

    def set_pending_clarification(self, pending: PendingClarification | None) -> None:
        self.pending_clarification = pending

    def mark_preview_stale(self) -> None:
        self.last_renderer_output = None
        self.last_preview_path = None
        if self.current_visual_plan is not None:
            self.current_visual_plan.metadata.is_preview_stale = True

    def clear_renderer_outputs(self) -> None:
        self.last_renderer_output = None
        self.last_preview_path = None
