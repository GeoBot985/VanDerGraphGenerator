"""Application state helpers."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from semantic_visual_builder.data.dataset_context import DatasetContext
from semantic_visual_builder.export.export_manager import ExportRequest
from semantic_visual_builder.export.export_result import ExportResult
from semantic_visual_builder.gallery.gallery_schema import GalleryItem
from semantic_visual_builder.image_style.style_extraction_result import (
    StyleExtractionResult,
)
from semantic_visual_builder.knowledge.graph_matrix import GraphMatrix
from semantic_visual_builder.knowledge.product_kb import ProductKnowledgeBase
from semantic_visual_builder.llm.llm_mapping_result import LlmMappingResult
from semantic_visual_builder.llm.model_registry import ModelRegistry
from semantic_visual_builder.llm.ollama_client import OllamaStatus
from semantic_visual_builder.planning.clarification import PendingClarification
from semantic_visual_builder.planning.semantic_trace import SemanticTrace
from semantic_visual_builder.planning.visual_plan_schema import VisualPlan
from semantic_visual_builder.planning.workflow_state import WorkflowState
from semantic_visual_builder.recipes.recipe_applier import RecipeApplicationResult
from semantic_visual_builder.recipes.recipe_compatibility import (
    RecipeCompatibilityReport,
)
from semantic_visual_builder.recipes.recipe_schema import VisualRecipe
from semantic_visual_builder.renderers.renderer_result import RendererOutput
from semantic_visual_builder.runtime.runtime_paths import RuntimePaths
from semantic_visual_builder.settings.settings_schema import AppSettings
from semantic_visual_builder.state.conversation_state import ConversationState
from semantic_visual_builder.state.revision_history import RevisionHistory
from semantic_visual_builder.styles.style_applier import StyleApplicationResult
from semantic_visual_builder.styles.style_comparison import StyleComparisonResult
from semantic_visual_builder.styles.style_review_model import EditableStyleDraft
from semantic_visual_builder.styles.style_schema import StyleProfile
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
    preview_status: str | None = None
    last_html_build_warnings: list[str] = field(default_factory=list)
    last_export_result: ExportResult | None = None
    llm_mapping_enabled: bool = True
    last_llm_mapping_result: LlmMappingResult | None = None
    last_mapping_method: str | None = None
    last_fallback_reason: str | None = None
    last_semantic_trace: SemanticTrace | None = None
    pending_clarification: PendingClarification | None = None
    active_recipe_path: Path | None = None
    active_recipe_name: str | None = None
    active_recipe: VisualRecipe | None = None
    recipe_compatibility_result: ValidationResult | None = None
    recipe_compatibility_report: RecipeCompatibilityReport | None = None
    recipe_application_result: RecipeApplicationResult | None = None
    available_recipes: list[VisualRecipe] = field(default_factory=list)
    active_style_profile: StyleProfile | None = None
    available_style_profiles: list[StyleProfile] = field(default_factory=list)
    style_application_result: StyleApplicationResult | None = None
    last_style_extraction_result: StyleExtractionResult | None = None
    selected_style_image_path: Path | None = None
    style_comparison_results: list[StyleComparisonResult] = field(default_factory=list)
    editable_style_draft: EditableStyleDraft | None = None
    last_imported_style_path: Path | None = None
    last_exported_style_path: Path | None = None
    vision_capable_models: list[str] = field(default_factory=list)
    app_settings: AppSettings = field(default_factory=AppSettings)
    gallery_items: list[GalleryItem] = field(default_factory=list)
    active_gallery_item: GalleryItem | None = None
    last_export_request: ExportRequest | None = None
    runtime_paths: RuntimePaths | None = None
    status_messages: list[str] = field(default_factory=list)

    def add_status(self, message: str) -> None:
        self.status_messages.append(message)

    def set_visual_plan(
        self, plan: VisualPlan, description: str = "Updated visual plan"
    ) -> None:
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
        self.preview_status = "Preview generated."

    def set_preview_path(self, path: Path) -> None:
        self.last_preview_path = path
        if self.current_visual_plan is not None:
            self.current_visual_plan.metadata.is_preview_stale = False
        self.preview_status = "Preview generated."

    def set_llm_mapping_enabled(self, enabled: bool) -> None:
        self.llm_mapping_enabled = enabled

    def set_pending_clarification(self, pending: PendingClarification | None) -> None:
        self.pending_clarification = pending

    def set_semantic_trace(self, trace: SemanticTrace | None) -> None:
        self.last_semantic_trace = trace

    def mark_preview_stale(self) -> None:
        self.last_renderer_output = None
        self.last_preview_path = None
        self.last_export_result = None
        self.last_html_build_warnings = []
        self.preview_status = "Preview stale. Regenerate to reflect latest plan."
        if self.current_visual_plan is not None:
            self.current_visual_plan.metadata.is_preview_stale = True

    def clear_renderer_outputs(self) -> None:
        self.last_renderer_output = None
        self.last_preview_path = None
        self.last_export_result = None
        self.last_html_build_warnings = []
        self.preview_status = "No visual plan yet."

    def set_preview_generated(
        self, path: Path, renderer_output: RendererOutput
    ) -> None:
        self.last_preview_path = path
        self.last_renderer_output = renderer_output
        self.preview_status = "Preview generated."

    def set_preview_failed(self, error: str) -> None:
        self.last_renderer_output = None
        self.last_preview_path = None
        self.last_export_result = None
        self.last_html_build_warnings = []
        self.preview_status = "Preview failed."
        self.add_status(error)

    def set_active_recipe(
        self, recipe: VisualRecipe | None, path: Path | None = None
    ) -> None:
        self.active_recipe = recipe
        self.active_recipe_path = path
        self.active_recipe_name = recipe.recipe_name if recipe is not None else None
        if recipe is None:
            self.recipe_compatibility_result = None
            self.recipe_compatibility_report = None
            self.recipe_application_result = None

    def set_active_style_profile(self, style: StyleProfile | None) -> None:
        self.active_style_profile = style

    def set_available_style_profiles(self, styles: list[StyleProfile]) -> None:
        self.available_style_profiles = list(styles)

    def set_style_extraction_result(self, result: StyleExtractionResult | None) -> None:
        self.last_style_extraction_result = result

    def set_selected_style_image_path(self, path: Path | None) -> None:
        self.selected_style_image_path = path

    def apply_style_to_current_plan(
        self, result: StyleApplicationResult | None
    ) -> None:
        self.style_application_result = result
        if result is None or result.visual_plan is None:
            return
        self.current_visual_plan = result.visual_plan
        self.mark_preview_stale()
        self.revision_history.add_revision(
            (
                "Applied style profile: "
                f"{result.visual_plan.metadata.style_profile_name or 'style'}"
            ),
            result.visual_plan,
            mapping_method=result.visual_plan.metadata.mapping_method,
            preview_stale=True,
        )
        self.last_renderer_output = None
        self.last_preview_path = None
        self.add_status("Style applied. Preview needs regeneration.")

    def set_recipe_compatibility_report(
        self, report: RecipeCompatibilityReport | None
    ) -> None:
        self.recipe_compatibility_report = report

    def set_recipe_application_result(
        self, result: RecipeApplicationResult | None
    ) -> None:
        self.recipe_application_result = result

    def set_editable_style_draft(self, draft: EditableStyleDraft | None) -> None:
        self.editable_style_draft = draft

    def set_style_comparison_results(
        self, results: list[StyleComparisonResult]
    ) -> None:
        self.style_comparison_results = list(results)

    def set_vision_capable_models(self, models: list[str]) -> None:
        self.vision_capable_models = list(models)

    def set_app_settings(self, settings: AppSettings) -> None:
        self.app_settings = settings

    def set_gallery_items(self, items: list[GalleryItem]) -> None:
        self.gallery_items = list(items)

    def set_active_gallery_item(self, item: GalleryItem | None) -> None:
        self.active_gallery_item = item

    def set_last_export_request(self, request: ExportRequest | None) -> None:
        self.last_export_request = request
