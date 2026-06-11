"""Tkinter desktop shell."""

from __future__ import annotations

import os
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, simpledialog, ttk

from semantic_visual_builder.data.csv_loader import CsvLoader
from semantic_visual_builder.data.data_profiler import DataProfiler
from semantic_visual_builder.export.html_exporter import HtmlExporter
from semantic_visual_builder.image_style import (
    ImageLoader,
    ImageStyleAnalyzer,
    ImageStyleExtractionOrchestrator,
    PaletteExtractor,
    StyleDraftBuilder,
    VlmStyleAnalyzer,
)
from semantic_visual_builder.knowledge.capability_answerer import CapabilityAnswerer
from semantic_visual_builder.llm.json_repair import JsonRepair
from semantic_visual_builder.llm.llm_response_parser import LlmResponseParser
from semantic_visual_builder.llm.llm_semantic_mapper import LlmSemanticMapper
from semantic_visual_builder.llm.ollama_client import OllamaClient
from semantic_visual_builder.llm.prompt_builder import VisualIntentPromptBuilder
from semantic_visual_builder.planning.clarification import PendingClarification
from semantic_visual_builder.planning.clarification_engine import ClarificationEngine
from semantic_visual_builder.planning.deterministic_fallback_mapper import (
    DeterministicFallbackMapper,
)
from semantic_visual_builder.planning.deterministic_fallback_patch_planner import (
    DeterministicFallbackPatchPlanner,
)
from semantic_visual_builder.planning.field_mapper import FieldMapper
from semantic_visual_builder.planning.planning_orchestrator import PlanningOrchestrator
from semantic_visual_builder.planning.refinement_orchestrator import (
    RefinementOrchestrator,
)
from semantic_visual_builder.planning.semantic_input_orchestrator import (
    SemanticInputOrchestrator,
    SemanticInputResult,
)
from semantic_visual_builder.planning.visual_plan import (
    summarize_visual_plan,
    visual_plan_to_dict,
)
from semantic_visual_builder.planning.visual_plan_patch_applier import (
    VisualPlanPatchApplier,
)
from semantic_visual_builder.planning.workflow_state import WorkflowStep
from semantic_visual_builder.recipes.recipe_applier import RecipeApplier
from semantic_visual_builder.recipes.recipe_builder import RecipeBuilder
from semantic_visual_builder.recipes.recipe_compatibility import (
    RecipeCompatibilityChecker,
)
from semantic_visual_builder.recipes.recipe_import_export import RecipeImportExport
from semantic_visual_builder.recipes.recipe_manager import RecipeManager
from semantic_visual_builder.recipes.recipe_mapping import RecipeFieldMapper
from semantic_visual_builder.recipes.recipe_store import RecipeStore
from semantic_visual_builder.recipes.recipe_validator import RecipeValidator
from semantic_visual_builder.renderers.chartjs_renderer import ChartJsRenderer
from semantic_visual_builder.renderers.mermaid_renderer import MermaidRenderer
from semantic_visual_builder.renderers.plotly_renderer import PlotlyRenderer
from semantic_visual_builder.renderers.python_renderer_future import (
    PythonRendererFuture,
)
from semantic_visual_builder.renderers.renderer_registry import RendererRegistry
from semantic_visual_builder.runtime.environment_report import build_environment_report
from semantic_visual_builder.state.app_state import AppState
from semantic_visual_builder.styles import (
    StyleApplier,
    StyleManager,
    StyleStore,
    StyleValidator,
)
from semantic_visual_builder.ui.about_dialog import show_about_dialog
from semantic_visual_builder.ui.error_dialog import show_error_dialog
from semantic_visual_builder.ui.preview_panel import PreviewPanel
from semantic_visual_builder.ui.recipe_panel import RecipePanel
from semantic_visual_builder.ui.status_panel import StatusPanel
from semantic_visual_builder.ui.style_extraction_panel import StyleExtractionPanel
from semantic_visual_builder.ui.style_panel import StylePanel
from semantic_visual_builder.ui.validation_panel import ValidationPanel
from semantic_visual_builder.ui.widgets import make_readonly_text, set_text
from semantic_visual_builder.utils.paths import (
    get_builtin_styles_dir,
    get_previews_dir,
    get_recipes_dir,
    get_user_styles_dir,
    get_webview_template_dir,
)
from semantic_visual_builder.validation.capability_validator import CapabilityValidator
from semantic_visual_builder.validation.llm_output_validator import LlmOutputValidator
from semantic_visual_builder.validation.visual_plan_validator import VisualPlanValidator
from semantic_visual_builder.version import APP_NAME, APP_VERSION
from semantic_visual_builder.webview.html_preview_host import HtmlPreviewHost
from semantic_visual_builder.webview.renderer_host import RendererHost


class SemanticVisualBuilderApp:
    """Minimal Tkinter shell for guided semantic visual planning."""

    def __init__(
        self, app_state: AppState, root: tk.Misc | None = None, build_ui: bool = True
    ):
        self.app_state = app_state
        self.csv_loader = CsvLoader()
        self.data_profiler = DataProfiler()
        self.deterministic_fallback_mapper = DeterministicFallbackMapper()
        self.field_mapper = FieldMapper()
        self.plan_validator = VisualPlanValidator()
        self.capability_validator = CapabilityValidator()
        self.capability_answerer = (
            CapabilityAnswerer(app_state.product_kb) if app_state.product_kb else None
        )
        self.ollama_client = OllamaClient()
        self.llm_mapper = LlmSemanticMapper(
            ollama_client=self.ollama_client,
            prompt_builder=VisualIntentPromptBuilder(),
            response_parser=LlmResponseParser(),
            output_validator=LlmOutputValidator(),
            json_repair=JsonRepair(),
        )
        self.planning_orchestrator = PlanningOrchestrator(
            llm_mapper=self.llm_mapper,
            deterministic_mapper=self.deterministic_fallback_mapper,
            field_mapper=self.field_mapper,
            visual_plan_validator=self.plan_validator,
            capability_validator=self.capability_validator,
        )
        self.refinement_orchestrator = RefinementOrchestrator(
            llm_mapper=self.llm_mapper,
            deterministic_fallback_patch_planner=DeterministicFallbackPatchPlanner(),
            patch_applier=VisualPlanPatchApplier(),
            visual_plan_validator=self.plan_validator,
            capability_validator=self.capability_validator,
            clarification_engine=ClarificationEngine(),
        )
        self.semantic_input_orchestrator = SemanticInputOrchestrator(
            planning_orchestrator=self.planning_orchestrator,
            refinement_orchestrator=self.refinement_orchestrator,
        )
        self.recipe_builder = RecipeBuilder()
        self.recipe_applier = RecipeApplier()
        self.recipe_store = RecipeStore(get_recipes_dir())
        self.recipe_validator = RecipeValidator()
        self.recipe_compatibility_checker = RecipeCompatibilityChecker()
        self.recipe_field_mapper = RecipeFieldMapper()
        self.recipe_manager = RecipeManager(
            self.recipe_store,
            self.recipe_validator,
            self.recipe_compatibility_checker,
            self.recipe_field_mapper,
            self.recipe_applier,
        )
        self.recipe_import_export = RecipeImportExport()
        self.style_store = StyleStore(get_user_styles_dir(), get_builtin_styles_dir())
        self.style_validator = StyleValidator()
        self.style_manager = StyleManager(self.style_store, self.style_validator)
        self.style_applier = StyleApplier()
        self.image_loader = ImageLoader()
        self.palette_extractor = PaletteExtractor()
        self.image_style_analyzer = ImageStyleAnalyzer()
        self.style_draft_builder = StyleDraftBuilder()
        self.vlm_style_analyzer = VlmStyleAnalyzer(self.ollama_client)
        self.image_style_orchestrator = ImageStyleExtractionOrchestrator(
            self.image_loader,
            self.palette_extractor,
            self.image_style_analyzer,
            self.style_draft_builder,
            self.style_validator,
            self.vlm_style_analyzer,
        )
        self.preview_panel = PreviewPanel()
        self.recipe_panel = RecipePanel()
        self.style_panel = StylePanel()
        self.style_extraction_panel = StyleExtractionPanel()
        self.status_panel = StatusPanel()
        self.validation_panel = ValidationPanel()
        self.renderer_registry = RendererRegistry(
            [
                PlotlyRenderer(),
                MermaidRenderer(),
                ChartJsRenderer(),
                PythonRendererFuture(),
            ]
        )
        self.renderer_host = RendererHost(get_webview_template_dir())
        self.html_exporter = HtmlExporter(get_previews_dir())
        self.preview_host = HtmlPreviewHost()
        self.conversation_state = self.app_state.conversation_state
        self.root = root or (tk.Tk() if build_ui else None)
        if self.root is None:
            return
        self.root.title(f"{APP_NAME} ({APP_VERSION})")
        self.root.geometry("1100x760")
        self._model_var = tk.StringVar(value="")
        self._status_var = tk.StringVar(value="")
        self._chat_var = tk.StringVar(value="")
        self._use_llm_var = tk.BooleanVar(value=self.app_state.llm_mapping_enabled)
        self._workflow_var = tk.StringVar(value="")
        self._revision_var = tk.StringVar(value="")
        self._mapping_method_var = tk.StringVar(
            value="Mapping method: deterministic_fallback"
        )
        self._fallback_reason_var = tk.StringVar(value="Fallback reason: none")
        self._clarification_var = tk.StringVar(value="No pending clarification.")
        self._clarification_answer_var = tk.StringVar(value="")
        self._style_var = tk.StringVar(value="")
        self._style_image_var = tk.StringVar(value="")
        self._style_image_model_var = tk.StringVar(value="")
        self._use_vision_var = tk.BooleanVar(value=False)
        self._build_ui()
        self._refresh_available_recipes()
        self._refresh_available_styles()
        self.refresh_ollama()
        self._refresh_all_views()

    def _build_ui(self) -> None:
        header = ttk.Label(
            self.root, text="Van Der Graph Generator", font=("Segoe UI", 18, "bold")
        )
        header.pack(anchor="w", padx=12, pady=(12, 6))

        self._build_menu()

        top = ttk.Frame(self.root)
        top.pack(fill="x", padx=12)
        self.status_label = ttk.Label(top, textvariable=self._status_var)
        self.status_label.pack(side="left")
        ttk.Label(top, text="Model:").pack(side="left", padx=(24, 6))
        self.model_combo = ttk.Combobox(
            top, textvariable=self._model_var, state="readonly", width=34
        )
        self.model_combo.pack(side="left")
        ttk.Checkbutton(
            top,
            text="Use LLM semantic mapping",
            variable=self._use_llm_var,
            command=self._on_toggle_llm_mapping,
        ).pack(side="left", padx=6)
        ttk.Label(top, textvariable=self._mapping_method_var).pack(side="left", padx=6)
        ttk.Button(top, text="Refresh Models", command=self.refresh_ollama).pack(
            side="left", padx=6
        )
        ttk.Button(top, text="Load CSV", command=self.load_csv).pack(
            side="left", padx=6
        )
        ttk.Button(top, text="Generate Preview", command=self.generate_preview).pack(
            side="left", padx=6
        )
        ttk.Button(top, text="Open Last Preview", command=self.open_last_preview).pack(
            side="left", padx=6
        )
        ttk.Button(
            top, text="Show Renderer Output", command=self.show_renderer_output
        ).pack(side="left", padx=6)
        ttk.Button(top, text="Save Recipe", command=self.save_recipe_action).pack(
            side="left", padx=6
        )
        ttk.Button(top, text="Load Recipe", command=self.load_recipe_action).pack(
            side="left", padx=6
        )
        ttk.Button(top, text="Apply Recipe", command=self.apply_recipe_action).pack(
            side="left", padx=6
        )
        ttk.Button(top, text="Clear Recipe", command=self.clear_recipe_action).pack(
            side="left", padx=6
        )

        style_row = ttk.Frame(self.root)
        style_row.pack(fill="x", padx=12, pady=(8, 0))
        ttk.Label(style_row, text="Style:").pack(side="left")
        self.style_combo = ttk.Combobox(
            style_row, textvariable=self._style_var, state="readonly", width=34
        )
        self.style_combo.pack(side="left", padx=(6, 6))
        ttk.Button(style_row, text="Apply Style", command=self.apply_style_action).pack(
            side="left", padx=6
        )
        ttk.Button(
            style_row, text="Save Current Style", command=self.save_style_action
        ).pack(side="left", padx=6)
        ttk.Button(style_row, text="Load Style", command=self.load_style_action).pack(
            side="left", padx=6
        )
        ttk.Button(style_row, text="Clear Style", command=self.clear_style_action).pack(
            side="left", padx=6
        )

        style_extract_row = ttk.Frame(self.root)
        style_extract_row.pack(fill="x", padx=12, pady=(6, 0))
        ttk.Label(style_extract_row, text="Style Image:").pack(side="left")
        self.style_image_combo = ttk.Combobox(
            style_extract_row,
            textvariable=self._style_image_model_var,
            width=30,
            state="readonly",
        )
        self.style_image_combo.pack(side="right", padx=(6, 0))
        ttk.Label(style_extract_row, text="Vision model:").pack(side="right")
        ttk.Checkbutton(
            style_extract_row,
            text="Use vision model if available",
            variable=self._use_vision_var,
        ).pack(side="right", padx=8)
        ttk.Button(
            style_extract_row,
            text="Apply Extracted Style",
            command=self.apply_extracted_style_action,
        ).pack(side="right", padx=6)
        ttk.Button(
            style_extract_row,
            text="Save Extracted Style",
            command=self.save_extracted_style_action,
        ).pack(side="right", padx=6)
        ttk.Button(
            style_extract_row,
            text="Extract Style",
            command=self.extract_style_action,
        ).pack(side="right", padx=6)
        ttk.Button(
            style_extract_row,
            text="Select Image",
            command=self.select_style_image_action,
        ).pack(side="right", padx=6)
        ttk.Entry(style_extract_row, textvariable=self._style_image_var, width=45).pack(
            side="right", padx=(6, 0)
        )

        status_frame = ttk.LabelFrame(self.root, text="Status")
        status_frame.pack(fill="x", padx=12, pady=(8, 0))
        self.status_summary = make_readonly_text(status_frame, height=4)
        self.status_summary.pack(fill="x", expand=True, padx=8, pady=6)

        middle = ttk.Frame(self.root)
        middle.pack(fill="both", expand=True, padx=12, pady=12)
        panes = ttk.Panedwindow(middle, orient=tk.HORIZONTAL)
        panes.pack(fill="both", expand=True)

        left = ttk.Frame(panes)
        right = ttk.Frame(panes)
        panes.add(left, weight=3)
        panes.add(right, weight=7)

        ttk.Label(left, text="Chat / Control").pack(anchor="w")
        self.chat_log = make_readonly_text(left, height=16)
        self.chat_log.pack(fill="both", expand=True, pady=(4, 8))
        entry_row = ttk.Frame(left)
        entry_row.pack(fill="x")
        self.chat_entry = ttk.Entry(entry_row, textvariable=self._chat_var)
        self.chat_entry.pack(side="left", fill="x", expand=True)
        ttk.Button(entry_row, text="Send", command=self.send_chat).pack(
            side="left", padx=6
        )

        ttk.Label(left, text="Clarification").pack(anchor="w", pady=(10, 0))
        self.clarification_text = make_readonly_text(left, height=7)
        self.clarification_text.pack(fill="both", expand=False, pady=(4, 6))
        clarification_row = ttk.Frame(left)
        clarification_row.pack(fill="x")
        self.clarification_entry = ttk.Entry(
            clarification_row, textvariable=self._clarification_answer_var
        )
        self.clarification_entry.pack(side="left", fill="x", expand=True)
        ttk.Button(
            clarification_row,
            text="Answer Clarification",
            command=self.answer_clarification_action,
        ).pack(side="left", padx=6)

        ttk.Label(right, text="Preview").pack(anchor="w")
        self.preview_text = make_readonly_text(right, height=4)
        self.preview_text.pack(fill="both", expand=False, pady=(4, 8))

        ttk.Label(right, text="Recipe").pack(anchor="w")
        self.recipe_text = make_readonly_text(right, height=5)
        self.recipe_text.pack(fill="both", expand=False, pady=(4, 8))

        ttk.Label(right, text="Style").pack(anchor="w")
        self.style_text = make_readonly_text(right, height=5)
        self.style_text.pack(fill="both", expand=False, pady=(4, 8))

        ttk.Label(right, text="Style Extraction").pack(anchor="w")
        self.style_extraction_text = make_readonly_text(right, height=7)
        self.style_extraction_text.pack(fill="both", expand=False, pady=(4, 8))

        ttk.Label(right, text="Dataset Profile").pack(anchor="w")
        self.profile_text = make_readonly_text(right, height=8)
        self.profile_text.pack(fill="both", expand=True, pady=(4, 8))

        ttk.Label(right, text="Current Visual Plan").pack(anchor="w")
        self.plan_text = make_readonly_text(right, height=8)
        self.plan_text.pack(fill="both", expand=True, pady=(4, 8))

        ttk.Label(right, text="Validation Result").pack(anchor="w")
        self.validation_text = make_readonly_text(right, height=6)
        self.validation_text.pack(fill="both", expand=True, pady=(4, 0))

        bottom = ttk.Frame(self.root)
        bottom.pack(fill="x", padx=12, pady=(0, 12))
        ttk.Label(bottom, textvariable=self._workflow_var).pack(anchor="w")
        ttk.Label(bottom, textvariable=self._revision_var).pack(anchor="w", pady=(0, 4))
        self.debug_text = make_readonly_text(bottom, height=6)
        self.debug_text.pack(fill="both", expand=False)

        self._append_preview("Preview placeholder")
        self._set_status("Startup complete.")

    def _build_menu(self) -> None:
        menu = tk.Menu(self.root)
        file_menu = tk.Menu(menu, tearoff=0)
        file_menu.add_command(label="Load CSV", command=self.load_csv)
        file_menu.add_command(
            label="Load Sample Dataset", command=self.load_sample_dataset
        )
        file_menu.add_command(label="Save Recipe", command=self.save_recipe_action)
        file_menu.add_command(label="Load Recipe", command=self.load_recipe_action)
        file_menu.add_command(label="Export HTML", command=self.export_html_action)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.destroy)
        menu.add_cascade(label="File", menu=file_menu)

        view_menu = tk.Menu(menu, tearoff=0)
        view_menu.add_command(
            label="Show Environment Report", command=self.show_environment_report
        )
        view_menu.add_command(label="Open Logs Folder", command=self.open_logs_folder)
        view_menu.add_command(
            label="Open Exports Folder", command=self.open_exports_folder
        )
        menu.add_cascade(label="View", menu=view_menu)

        help_menu = tk.Menu(menu, tearoff=0)
        help_menu.add_command(
            label="About", command=lambda: show_about_dialog(self.root)
        )
        help_menu.add_command(
            label="Troubleshooting", command=self.show_troubleshooting
        )
        menu.add_cascade(label="Help", menu=help_menu)
        self.root.config(menu=menu)

    def refresh_ollama(self) -> None:
        from semantic_visual_builder.llm.ollama_client import OllamaClient

        client = OllamaClient()
        status = client.get_status()
        models = client.list_models() if status.is_connected else []
        self.app_state.ollama_status = status
        self.app_state.model_registry.set_models(models)
        self._model_var.set(self.app_state.model_registry.selected_model or "")
        model_names = self.app_state.model_registry.get_model_names()
        self.model_combo["values"] = model_names
        if hasattr(self, "style_image_combo"):
            self.style_image_combo["values"] = model_names
            selected_image_model = self._style_image_model_var.get().strip()
            if selected_image_model not in model_names:
                self._style_image_model_var.set(
                    self.app_state.model_registry.selected_model
                    or (model_names[0] if model_names else "")
                )
        if status.is_connected:
            self._set_status("Ollama connected.")
        else:
            self._set_status(
                "Ollama not connected. Start Ollama and click Refresh Models."
            )
        self._refresh_all_views()

    def load_csv(self) -> None:
        if self.app_state.runtime_paths is not None:
            initial_dir = self.app_state.runtime_paths.asset_dir / "samples"
        else:
            initial_dir = Path.cwd() / "assets" / "samples"
        filename = filedialog.askopenfilename(
            filetypes=[("CSV files", "*.csv")], initialdir=str(initial_dir)
        )
        if not filename:
            return
        self._load_csv_path(Path(filename))

    def load_sample_dataset(self) -> str:
        if self.app_state.runtime_paths is not None:
            sample_path = (
                self.app_state.runtime_paths.asset_dir
                / "samples"
                / "sample_transactions.csv"
            )
        else:
            sample_path = Path.cwd() / "assets" / "samples" / "sample_transactions.csv"
        if not sample_path.exists():
            message = f"Sample dataset not found: {sample_path}"
            self.app_state.add_status(message)
            show_error_dialog("Sample dataset missing", message, parent=self.root)
            return message
        self._load_csv_path(sample_path)
        return f"Loaded sample dataset: {sample_path.name}"

    def _load_csv_path(self, path: Path) -> None:
        loaded = self.csv_loader.load(path=path)
        profile = self.data_profiler.profile(loaded.dataframe)
        self.app_state.dataset_context.loaded_dataset = loaded
        self.app_state.dataset_context.profile = profile
        self.app_state.current_visual_plan = None
        self.app_state.current_validation_result = None
        self.app_state.clear_renderer_outputs()
        self.app_state.set_pending_clarification(None)
        self.app_state.set_active_recipe(None)
        self.app_state.workflow_state.advance_to(WorkflowStep.VISUAL_GOAL_REQUIRED)
        self.app_state.add_status(f"Loaded CSV: {loaded.path.name}")
        self._append_preview(f"Loaded dataset: {loaded.path.name}")
        self._refresh_all_views()

    def send_chat(self) -> None:
        content = self._chat_var.get().strip()
        if not content:
            return
        self._chat_var.set("")
        self.conversation_state.add_user_message(content)
        self._append_chat(f"User: {content}")

        if self.app_state.pending_clarification is not None:
            response = self._handle_clarification_answer(content)
        else:
            semantic_result = self.semantic_input_orchestrator.handle_message(
                content,
                self.app_state,
                use_llm=self._use_llm_var.get(),
            )
            response = self._handle_semantic_result(content, semantic_result)
        self._append_assistant_response(response)
        self._refresh_all_views()

    def _handle_semantic_result(self, content: str, result: SemanticInputResult) -> str:
        self.app_state.current_validation_result = result.validation_result
        self.app_state.last_llm_mapping_result = result.llm_mapping_result
        self.app_state.last_mapping_method = result.mapping_method
        self.app_state.last_fallback_reason = (
            "; ".join(result.messages) if result.used_fallback else None
        )
        for message in result.messages:
            self.app_state.add_status(message)
        if hasattr(self, "_status_var"):
            self._status_var.set(
                f"Semantic input handled: {result.action} ({result.mapping_method})"
            )

        if result.action == "capability_question":
            return self._answer_capability_question(content)
        if result.action == "workflow_help":
            return self._workflow_help_text()
        if result.action == "clarification_request":
            if result.clarification_requests:
                request = result.clarification_requests[0]
                pending = PendingClarification(
                    request=request,
                    partial_plan_json=None
                    if self.app_state.current_visual_plan is None
                    else visual_plan_to_dict(self.app_state.current_visual_plan),
                    partial_plan_id=self.app_state.current_visual_plan.metadata.plan_id
                    if self.app_state.current_visual_plan
                    else None,
                )
                self.app_state.set_pending_clarification(pending)
                self._update_clarification_view()
                return self._clarification_prompt_text(request)
            return "I need one more detail before I can update the plan."
        if result.action == "unsupported":
            return "The requested visual is not supported by the graph matrix contract."

        if result.visual_plan is None:
            return "No visual plan could be created."

        self.app_state.set_visual_plan(
            result.visual_plan,
            description=(
                "Refined visual plan"
                if result.action == "refinement_request"
                else "Updated visual plan"
            ),
        )
        if result.action == "refinement_request":
            self.app_state.workflow_state.advance_to(
                WorkflowStep.REFINEMENT_LOOP
                if result.validation_result.is_valid
                else WorkflowStep.FIELD_MAPPING_CONFIRMED
            )
        else:
            self.app_state.workflow_state.advance_to(
                WorkflowStep.PLAN_READY
                if result.validation_result.is_valid
                else WorkflowStep.FIELD_MAPPING_CONFIRMED
            )
        return self._visual_plan_response(result.visual_plan, result.validation_result)

    def _answer_capability_question(self, question: str) -> str:
        if self.capability_answerer is None:
            return (
                "Capability answers are unavailable until the product knowledge "
                "base loads."
            )
        answer = self.capability_answerer.answer(question)
        self.app_state.add_status("Answered capability question from Product KB.")
        return answer

    def _workflow_help_text(self) -> str:
        workflow = (
            self.app_state.product_kb.workflow.get("workflow", [])
            if self.app_state.product_kb
            else []
        )
        if not workflow:
            return (
                "Load data, describe the visual goal, confirm the plan, then refine it."
            )
        lines = ["Guided workflow:"]
        for step in workflow:
            if isinstance(step, dict):
                lines.append(
                    f"{step.get('step')}. {step.get('name')}: {step.get('description')}"
                )
        self.app_state.add_status("Displayed workflow guidance.")
        return "\n".join(lines)

    def _handle_visual_request(self, content: str) -> str:
        return self._run_planning(content, is_refinement=False)

    def _handle_refinement_request(self, content: str) -> str:
        if self.app_state.current_visual_plan is None:
            return "Create a visual plan first, then I can apply refinements."
        return self._run_refinement(content)

    def _run_planning(self, content: str, is_refinement: bool) -> str:
        use_llm = self._use_llm_var.get() and bool(
            self.app_state.model_registry.selected_model
        )
        if not self._use_llm_var.get():
            self.app_state.add_status(
                "I could not use LLM semantic mapping because it is disabled. "
                "I used the limited deterministic fallback instead."
            )
        elif (
            self._use_llm_var.get() and not self.app_state.model_registry.selected_model
        ):
            self.app_state.add_status(
                "I could not use LLM semantic mapping because no model is "
                "selected. I used the limited deterministic fallback instead."
            )
        result = self.planning_orchestrator.create_or_update_plan(
            user_message=content,
            app_state=self.app_state,
            use_llm=use_llm,
        )
        if result.visual_plan is not None:
            self.app_state.set_visual_plan(
                result.visual_plan, description="Updated visual plan"
            )
        self.app_state.current_validation_result = result.validation_result
        self.app_state.last_llm_mapping_result = result.llm_mapping_result
        self.app_state.last_mapping_method = result.mapping_method
        self.app_state.last_fallback_reason = (
            "; ".join(result.messages)
            if result.used_fallback or result.messages
            else None
        )
        self.app_state.workflow_state.advance_to(
            (WorkflowStep.REFINEMENT_LOOP if is_refinement else WorkflowStep.PLAN_READY)
            if result.validation_result.is_valid
            else WorkflowStep.FIELD_MAPPING_CONFIRMED
        )
        if result.used_fallback:
            self.app_state.add_status(
                "LLM mapping failed. Falling back to deterministic fallback mapping."
            )
        for message in result.messages:
            self.app_state.add_status(message)
        validation = result.validation_result
        plan = result.visual_plan
        if plan is None:
            return "No visual plan could be created."
        return self._visual_plan_response(plan, validation)

    def _run_refinement(self, content: str) -> str:
        current_plan = self.app_state.current_visual_plan
        if current_plan is None:
            return "Create a visual plan first, then I can apply refinements."
        use_llm = self._use_llm_var.get() and bool(
            self.app_state.model_registry.selected_model
        )
        if not self._use_llm_var.get():
            self.app_state.add_status(
                "I could not use LLM semantic refinement because it is "
                "disabled. I used deterministic fallback patch planning where "
                "possible."
            )
        elif (
            self._use_llm_var.get() and not self.app_state.model_registry.selected_model
        ):
            self.app_state.add_status(
                "I could not use LLM semantic refinement because no model is "
                "selected. I used deterministic fallback patch planning where "
                "possible."
            )
        result = self.refinement_orchestrator.refine_plan(
            current_plan=current_plan,
            user_message=content,
            app_state=self.app_state,
            use_llm=use_llm,
        )
        self.app_state.current_validation_result = result.validation_result
        self.app_state.last_mapping_method = result.mapping_method
        self.app_state.last_fallback_reason = (
            "; ".join(result.messages)
            if result.used_fallback or result.messages
            else None
        )
        if result.visual_plan is not None:
            self.app_state.set_visual_plan(
                result.visual_plan, description="Refined visual plan"
            )
        for message in result.messages:
            self.app_state.add_status(message)
        if result.clarification_requests:
            request = result.clarification_requests[0]
            pending = PendingClarification(
                request=request,
                partial_plan_json=None
                if self.app_state.current_visual_plan is None
                else visual_plan_to_dict(self.app_state.current_visual_plan),
                partial_plan_id=self.app_state.current_visual_plan.metadata.plan_id
                if self.app_state.current_visual_plan
                else None,
            )
            self.app_state.set_pending_clarification(pending)
            self._update_clarification_view()
            return self._clarification_prompt_text(request)
        if result.visual_plan is None:
            return "No refined visual plan could be accepted."
        self.app_state.workflow_state.advance_to(
            WorkflowStep.REFINEMENT_LOOP
            if result.validation_result.is_valid
            else WorkflowStep.FIELD_MAPPING_CONFIRMED
        )
        return self._visual_plan_response(result.visual_plan, result.validation_result)

    def _handle_clarification_answer(self, content: str) -> str:
        pending = self.app_state.pending_clarification
        if pending is None or self.app_state.current_visual_plan is None:
            return "There is no pending clarification."
        clarified = ClarificationEngine().apply_answer(
            self.app_state.current_visual_plan, pending.request, content
        )
        self.app_state.set_pending_clarification(None)
        self.app_state.set_visual_plan(
            clarified, description="Applied clarification answer"
        )
        self.app_state.current_validation_result = self.plan_validator.validate(
            clarified,
            self.app_state.dataset_context.profile,
            self.app_state.graph_matrix,
        )
        self.app_state.add_status("Clarification answer applied.")
        self._update_clarification_view()
        return self._visual_plan_response(
            clarified, self.app_state.current_validation_result
        )

    def _clarification_prompt_text(self, request) -> str:
        lines = [
            "Clarification needed:",
            request.question,
            "",
            "Options:",
        ]
        if request.options:
            lines.extend([f"- {option.label}" for option in request.options])
        else:
            lines.append("- Free text answer")
        return "\n".join(lines)

    def generate_preview(self) -> str:
        plan = self.app_state.current_visual_plan
        validation = self.app_state.current_validation_result
        if plan is None or validation is None or not validation.is_valid:
            message = (
                "No valid visual plan is ready. Load data and describe the visual "
                "first."
            )
            self.app_state.add_status(message)
            self._refresh_all_views()
            return message

        try:
            renderer = self.renderer_registry.get_renderer(plan)
            renderer_output = renderer.render(plan, self.app_state.dataset_context)
            renderer_validation = renderer.validate_output(renderer_output)
            if not renderer_validation.is_valid:
                message = (
                    "Preview could not be generated: renderer output validation failed."
                )
                self.app_state.add_status(message)
                self.app_state.set_preview_failed(message)
                self._refresh_all_views()
                return message

            build_result = self.renderer_host.build_html(renderer_output)
            self.app_state.last_html_build_warnings = list(build_result.warnings)
            for warning in build_result.warnings:
                self.app_state.add_status(warning)
            export_result = self.html_exporter.export_html(build_result.html)
            self.app_state.last_export_result = export_result
            if not export_result.success or export_result.path is None:
                message = export_result.error or "HTML export failed."
                self.app_state.set_preview_failed(message)
                self._refresh_all_views()
                return message
            self.app_state.set_preview_generated(export_result.path, renderer_output)
            self.preview_host.open_preview(export_result.path)
            self.app_state.add_status(f"Preview generated: {export_result.path}")
            self._refresh_all_views()
            return f"Preview generated: {export_result.path}"
        except Exception as exc:
            message = f"Preview could not be generated: {exc}"
            self.app_state.set_preview_failed(message)
            self.app_state.add_status(message)
            show_error_dialog(
                "Preview error",
                "Preview could not be generated.",
                str(exc),
                parent=self.root,
            )
            self._refresh_all_views()
            return message

    def open_last_preview(self) -> str:
        path = self.app_state.last_preview_path
        if path is None:
            message = "No preview file has been generated yet."
            self.app_state.add_status(message)
            self._refresh_all_views()
            return message
        self.preview_host.open_preview(path)
        message = f"Opened preview: {path}"
        self.app_state.add_status(message)
        self._refresh_all_views()
        return message

    def show_renderer_output(self) -> str:
        text = self._renderer_output_text()
        self.app_state.add_status("Renderer output displayed.")
        self._refresh_all_views()
        return text

    def export_html_action(self) -> str:
        if self.app_state.last_preview_path is None:
            message = "Generate a preview before exporting HTML."
            self.app_state.add_status(message)
            self._refresh_all_views()
            return message
        os.startfile(self.app_state.last_preview_path)
        message = f"Opened exported HTML: {self.app_state.last_preview_path}"
        self.app_state.add_status(message)
        self._refresh_all_views()
        return message

    def show_environment_report(self) -> str:
        if self.app_state.runtime_paths is None:
            message = "Runtime paths are unavailable."
        else:
            message = build_environment_report(
                self.app_state.runtime_paths, self.app_state
            )
        self.app_state.add_status("Environment report displayed.")
        messagebox.showinfo(f"{APP_NAME} Environment Report", message, parent=self.root)
        return message

    def open_logs_folder(self) -> str:
        if self.app_state.runtime_paths is None:
            return "Runtime paths are unavailable."
        os.startfile(self.app_state.runtime_paths.log_dir)
        return f"Opened logs folder: {self.app_state.runtime_paths.log_dir}"

    def open_exports_folder(self) -> str:
        if self.app_state.runtime_paths is None:
            return "Runtime paths are unavailable."
        os.startfile(self.app_state.runtime_paths.export_dir)
        return f"Opened exports folder: {self.app_state.runtime_paths.export_dir}"

    def show_troubleshooting(self) -> str:
        message = (
            "Troubleshooting:\n"
            "- Start Ollama before using LLM features.\n"
            "- Load a CSV before creating a chart.\n"
            "- If local assets are missing, CDN fallback is used.\n"
            "- Recipes must match the active dataset."
        )
        messagebox.showinfo("Troubleshooting", message, parent=self.root)
        return message

    def _visual_plan_response(self, plan, validation) -> str:
        return (
            "I interpreted this as a neutral visual plan.\n\n"
            f"{summarize_visual_plan(plan)}\n\n"
            f"Validation:\n{self._format_validation(validation)}\n\n"
            "Rendering starts in a later sprint."
        )

    def _append_chat(self, text: str) -> None:
        self.chat_log.configure(state="normal")
        self.chat_log.insert("end", text + "\n")
        self.chat_log.configure(state="disabled")

    def _append_assistant_response(self, text: str) -> None:
        self.conversation_state.add_assistant_message(text)
        self._append_chat(f"Assistant: {text}")

    def _append_preview(self, text: str) -> None:
        set_text(self.preview_text, text)

    def _update_profile_view(self) -> None:
        profile = self.app_state.dataset_context.profile
        if profile is None:
            set_text(self.profile_text, "No dataset loaded.")
            return
        lines = [f"Rows: {profile.row_count}", f"Columns: {profile.column_count}", ""]
        for column in profile.columns:
            details = (
                f"{column.name} | {column.dtype} | {column.semantic_type} | "
                f"nulls={column.null_count} | uniques={column.unique_count}"
            )
            lines.append(details)
        set_text(self.profile_text, "\n".join(lines))

    def _update_plan_view(self) -> None:
        plan = self.app_state.current_visual_plan
        set_text(
            self.plan_text,
            summarize_visual_plan(plan) if plan is not None else "No visual plan yet.",
        )

    def _update_preview_view(self) -> None:
        lines = [self.preview_panel.preview_status_text(self.app_state)]
        if self.app_state.last_preview_path is not None:
            lines.append(f"Last preview path: {self.app_state.last_preview_path}")
        if self.app_state.last_html_build_warnings:
            lines.append("")
            lines.append("HTML build warnings:")
            lines.extend(
                f"- {warning}" for warning in self.app_state.last_html_build_warnings
            )
        set_text(self.preview_text, "\n".join(lines))

    def _update_recipe_view(self) -> None:
        set_text(
            self.recipe_text,
            "\n".join(
                [
                    self.recipe_panel.active_recipe_text(self.app_state),
                    "",
                    self.recipe_panel.compatibility_text(self.app_state),
                ]
            ),
        )

    def _update_style_view(self) -> None:
        set_text(
            self.style_text,
            "\n".join(
                [
                    self.style_panel.active_style_text(self.app_state),
                    "",
                    self.style_panel.available_styles_text(self.app_state),
                ]
            ),
        )

    def _update_style_extraction_view(self) -> None:
        if not hasattr(self, "style_extraction_text"):
            return
        set_text(
            self.style_extraction_text,
            "\n\n".join(
                [
                    self.style_extraction_panel.image_text(self.app_state),
                    self.style_extraction_panel.summary_text(self.app_state),
                ]
            ),
        )

    def _update_validation_view(self) -> None:
        validation = self.app_state.current_validation_result
        set_text(
            self.validation_text,
            self.validation_panel.validation_text(self.app_state)
            if validation is not None
            else "No validation result yet.",
        )

    def _update_clarification_view(self) -> None:
        if not hasattr(self, "clarification_text"):
            return
        pending = self.app_state.pending_clarification
        if pending is None:
            set_text(self.clarification_text, "No pending clarification.")
            return
        lines = [
            "Clarification needed:",
            pending.request.question,
            "",
            f"Reason: {pending.request.reason}",
        ]
        if pending.request.options:
            lines.extend(["", "Options:"])
            lines.extend(f"- {option.label}" for option in pending.request.options)
        set_text(self.clarification_text, "\n".join(lines))

    def _update_workflow_view(self) -> None:
        self._workflow_var.set(
            f"Workflow step: {self.app_state.workflow_state.current_step.value}"
        )
        self._revision_var.set(
            f"Revision count: {self.app_state.revision_history.count()}"
        )
        mapping_method = self.app_state.last_mapping_method or "deterministic_fallback"
        self._mapping_method_var.set(f"Mapping method: {mapping_method}")
        fallback_reason = self.app_state.last_fallback_reason or "none"
        self._fallback_reason_var.set(f"Fallback reason: {fallback_reason}")

    def _refresh_debug(self) -> None:
        lines = list(self.app_state.status_messages)
        if self.app_state.last_semantic_trace is not None:
            lines.append("Latest semantic trace:")
            lines.extend(self.app_state.last_semantic_trace.to_lines())
        if self.app_state.ollama_status:
            lines.append(
                f"Ollama connected: {self.app_state.ollama_status.is_connected}"
            )
            if self.app_state.ollama_status.version:
                lines.append(f"Ollama version: {self.app_state.ollama_status.version}")
            if self.app_state.ollama_status.error:
                lines.append(f"Ollama error: {self.app_state.ollama_status.error}")
        elif self.app_state.ollama_status is None:
            lines.append("Ollama status: unavailable")
        else:
            if self.app_state.ollama_status.error:
                lines.append(f"Ollama error: {self.app_state.ollama_status.error}")
        mapping_state = "Enabled" if self.app_state.llm_mapping_enabled else "Disabled"
        lines.append(f"LLM semantic mapping: {mapping_state}")
        lines.append(
            f"Selected model: {self.app_state.model_registry.selected_model or 'None'}"
        )
        lines.append(self._mapping_method_var.get())
        lines.append(self._fallback_reason_var.get())
        if self.app_state.last_llm_mapping_result is not None:
            lines.append("LLM raw response:")
            lines.extend(
                self.app_state.last_llm_mapping_result.raw_response.splitlines()[:10]
                or ["<empty>"]
            )
            lines.append("Parsed LLM JSON:")
            lines.append(str(self.app_state.last_llm_mapping_result.parsed_json))
        if self.app_state.pending_clarification is not None:
            lines.append("Pending clarification:")
            lines.append(self.app_state.pending_clarification.request.question)
        if self.app_state.current_visual_plan is not None:
            lines.append("Final VisualPlan:")
            lines.extend(
                summarize_visual_plan(self.app_state.current_visual_plan).splitlines()
            )
        if self.app_state.current_validation_result is not None:
            lines.append("Validation result:")
            lines.append(
                self._format_validation(self.app_state.current_validation_result)
            )
        lines.extend(self._renderer_debug_lines())
        set_text(self.debug_text, "\n".join(lines) or "Ready.")

    def _refresh_all_views(self) -> None:
        if self.root is None:
            return
        self._refresh_available_recipes()
        self._refresh_available_styles()
        self._update_profile_view()
        self._update_plan_view()
        self._update_preview_view()
        self._update_recipe_view()
        self._update_style_view()
        self._update_style_extraction_view()
        self._update_validation_view()
        self._update_clarification_view()
        self._update_workflow_view()
        set_text(self.status_summary, self.status_panel.status_text(self.app_state))
        self._refresh_debug()

    def _refresh_available_recipes(self) -> None:
        try:
            self.app_state.available_recipes = [
                self.recipe_store.load_recipe(path)
                for path in self.recipe_store.list_recipes()
            ]
        except Exception as exc:
            self.app_state.available_recipes = []
            self.app_state.add_status(f"Recipe catalog could not be loaded: {exc}")

    def _refresh_available_styles(self) -> None:
        try:
            styles = self.style_manager.list_styles()
            self.app_state.set_available_style_profiles(styles)
            self.style_combo["values"] = [style.style_name for style in styles]
            if self.app_state.active_style_profile is not None:
                self._style_var.set(self.app_state.active_style_profile.style_name)
            else:
                self._style_var.set("")
        except Exception as exc:
            self.app_state.set_available_style_profiles([])
            self.app_state.add_status(f"Style catalog could not be loaded: {exc}")

    def _set_status(self, message: str) -> None:
        self._status_var.set(message)
        self.app_state.add_status(message)
        self._refresh_debug()

    def _format_validation(self, validation) -> str:
        if validation is None:
            return "No validation result yet."
        if not validation.messages:
            return "Plan is valid."
        return "\n".join(
            f"{item.severity.value.upper()}: {item.message}"
            for item in validation.messages
        )

    def _renderer_debug_lines(self) -> list[str]:
        lines: list[str] = []
        output = self.app_state.last_renderer_output
        if output is not None:
            lines.append(f"Renderer: {output.renderer_name}")
            lines.append(f"Output type: {output.output_type}")
        if self.app_state.last_preview_path is not None:
            lines.append(f"Preview file: {self.app_state.last_preview_path}")
        renderer_output_text = self._renderer_output_text()
        if renderer_output_text:
            lines.append("Renderer output:")
            lines.extend(renderer_output_text.splitlines())
        return lines

    def _renderer_output_text(self) -> str:
        output = self.app_state.last_renderer_output
        if output is None:
            return "No renderer output yet."
        content = output.content
        return content if len(content) <= 2000 else content[:2000] + "..."

    def _on_toggle_llm_mapping(self) -> None:
        self.app_state.set_llm_mapping_enabled(self._use_llm_var.get())
        state = "enabled" if self._use_llm_var.get() else "disabled"
        self.app_state.add_status(f"LLM semantic mapping {state}.")
        self._refresh_all_views()

    def answer_clarification_action(self) -> str:
        answer = self._clarification_answer_var.get().strip()
        if not answer:
            message = "Enter an answer for the pending clarification."
            self.app_state.add_status(message)
            self._refresh_all_views()
            return message
        self._clarification_answer_var.set("")
        return self._handle_clarification_answer(answer)

    def save_recipe_action(self) -> str:
        plan = self.app_state.current_visual_plan
        validation = self.app_state.current_validation_result
        if plan is None or validation is None or not validation.is_valid:
            message = "Create a valid visual plan before saving a recipe."
            self.app_state.add_status(message)
            self._refresh_all_views()
            return message
        recipe_name = simpledialog.askstring("Save Recipe", "Recipe name:")
        if not recipe_name:
            return "Recipe save cancelled."
        recipe = self.recipe_builder.build_from_current_plan(
            recipe_name=recipe_name,
            visual_plan=plan,
            dataset_profile=self.app_state.dataset_context.profile,
            description=f"Recipe created from {recipe_name}",
        )
        recipe_result = self.recipe_validator.validate_recipe(recipe)
        if not recipe_result.is_valid:
            message = self._format_validation(recipe_result)
            self.app_state.add_status(message)
            self._refresh_all_views()
            return message
        path = self.recipe_store.save_recipe(recipe)
        self.app_state.set_active_recipe(recipe, path)
        self._refresh_available_recipes()
        message = f"Recipe saved: {path}"
        self.app_state.add_status(message)
        self._refresh_all_views()
        return message

    def load_recipe_action(self) -> str:
        filename = filedialog.askopenfilename(
            filetypes=[("Recipe files", "*.recipe.json")]
        )
        if not filename:
            return "Recipe load cancelled."
        path = Path(filename)
        recipe = self.recipe_store.load_recipe(path)
        if self.app_state.dataset_context.profile is not None:
            report = self.recipe_compatibility_checker.check_compatibility(
                recipe, self.app_state.dataset_context.profile
            )
            self.app_state.set_recipe_compatibility_report(report)
            validation = self.recipe_validator.validate_against_dataset(
                recipe, self.app_state.dataset_context.profile
            )
            self.app_state.recipe_compatibility_result = validation
        else:
            validation = self.recipe_validator.validate_recipe(recipe)
            self.app_state.recipe_compatibility_result = validation
            self.app_state.set_recipe_compatibility_report(None)
        self.app_state.set_active_recipe(recipe, path)
        self.app_state.add_status(f"Recipe loaded: {recipe.recipe_name}")
        self._refresh_all_views()
        if validation.is_valid:
            return f"Recipe loaded: {recipe.recipe_name}"
        return self._format_validation(validation)

    def apply_recipe_action(self) -> str:
        recipe = self.app_state.active_recipe
        profile = self.app_state.dataset_context.profile
        if recipe is None:
            message = "Load a recipe first."
            self.app_state.add_status(message)
            self._refresh_all_views()
            return message
        if profile is None:
            message = "Load a dataset before applying a recipe."
            self.app_state.add_status(message)
            self._refresh_all_views()
            return message
        result = self.recipe_manager.propose_and_apply(recipe, profile)
        self.app_state.set_recipe_application_result(result)
        self.app_state.set_recipe_compatibility_report(result.compatibility_report)
        self.app_state.recipe_compatibility_result = (
            self.recipe_validator.validate_against_dataset(recipe, profile)
        )
        if not result.success or result.visual_plan is None:
            message = (
                "; ".join(result.errors)
                if result.errors
                else "Recipe application failed."
            )
            self.app_state.add_status(message)
            self._refresh_all_views()
            return message
        self.app_state.set_visual_plan(
            result.visual_plan, description=f"Applied recipe: {recipe.recipe_name}"
        )
        self.app_state.current_validation_result = self.plan_validator.validate(
            result.visual_plan,
            self.app_state.dataset_context.profile,
            self.app_state.graph_matrix,
        )
        self.app_state.last_fallback_reason = (
            "; ".join(result.warnings) if result.warnings else None
        )
        self.app_state.add_status(f"Recipe applied: {recipe.recipe_name}")
        self._refresh_all_views()
        return f"Recipe applied: {recipe.recipe_name}"

    def clear_recipe_action(self) -> str:
        self.app_state.set_active_recipe(None)
        self.app_state.recipe_compatibility_result = None
        self.app_state.set_recipe_compatibility_report(None)
        self.app_state.set_recipe_application_result(None)
        self.app_state.add_status("Recipe cleared.")
        self._refresh_all_views()
        return "Recipe cleared."

    def apply_style_action(self) -> str:
        style = self._selected_style_profile()
        if style is None:
            message = "Select a style profile first."
            self.app_state.add_status(message)
            self._refresh_all_views()
            return message
        self.app_state.set_active_style_profile(style)
        if self.app_state.current_visual_plan is None:
            self.app_state.add_status(f"Style selected: {style.style_name}")
            self._refresh_all_views()
            return f"Style selected: {style.style_name}"
        result = self.style_applier.apply_style(
            self.app_state.current_visual_plan, style
        )
        self.app_state.apply_style_to_current_plan(result)
        if not result.success or result.visual_plan is None:
            message = (
                "; ".join(result.errors)
                if result.errors
                else "Style application failed."
            )
            self.app_state.add_status(message)
            self._refresh_all_views()
            return message
        self.app_state.add_status(f"Style applied: {style.style_name}")
        self._style_var.set(style.style_name)
        self._refresh_all_views()
        return f"Style applied: {style.style_name}"

    def save_style_action(self) -> str:
        style = self.app_state.active_style_profile or self._style_profile_from_plan()
        if style is None:
            message = "Create or select a style first."
            self.app_state.add_status(message)
            self._refresh_all_views()
            return message
        style_name = simpledialog.askstring(
            "Save Style Profile", "Style name:", initialvalue=style.style_name
        )
        if not style_name:
            return "Style save cancelled."
        style.metadata.style_name = style_name
        style.metadata.style_id = self.style_store._safe_name(style_name)
        path = self.style_manager.save_style(style)
        self.app_state.add_status(f"Style saved: {path}")
        self._refresh_available_styles()
        self._refresh_all_views()
        return f"Style saved: {path}"

    def load_style_action(self) -> str:
        filename = filedialog.askopenfilename(
            filetypes=[("Style files", "*.style.json")]
        )
        if not filename:
            return "Style load cancelled."
        style = self.style_store.load_style(Path(filename))
        validation = self.style_manager.validate_style(style)
        if not validation.is_valid:
            message = self._format_validation(validation)
            self.app_state.add_status(message)
            self._refresh_all_views()
            return message
        self.app_state.set_active_style_profile(style)
        self._style_var.set(style.style_name)
        self.app_state.add_status(f"Style loaded: {style.style_name}")
        self._refresh_all_views()
        return f"Style loaded: {style.style_name}"

    def clear_style_action(self) -> str:
        self.app_state.set_active_style_profile(None)
        self.app_state.apply_style_to_current_plan(None)
        self._style_var.set("")
        self.app_state.add_status("Style cleared.")
        self._refresh_all_views()
        return "Style cleared."

    def select_style_image_action(self) -> str:
        if self.app_state.runtime_paths is not None:
            initial_dir = self.app_state.runtime_paths.asset_dir / "samples"
        else:
            initial_dir = Path.cwd() / "assets" / "samples"
        filename = filedialog.askopenfilename(
            filetypes=[
                ("Image files", "*.png *.jpg *.jpeg *.webp"),
                ("All files", "*.*"),
            ],
            initialdir=str(initial_dir),
        )
        if not filename:
            return "Style image selection cancelled."
        path = Path(filename)
        self.app_state.set_selected_style_image_path(path)
        self._style_image_var.set(str(path))
        self.app_state.add_status(f"Style image selected: {path.name}")
        self._refresh_all_views()
        return f"Style image selected: {path.name}"

    def extract_style_action(self) -> str:
        selected = self._style_image_var.get().strip()
        if not selected:
            selection_message = self.select_style_image_action()
            if "cancelled" in selection_message.lower():
                return selection_message
            selected = self._style_image_var.get().strip()
        if not selected:
            message = "Select a style image first."
            self.app_state.add_status(message)
            self._refresh_all_views()
            return message
        image_path = Path(selected)
        if not image_path.exists():
            message = f"Image file not found: {image_path}"
            self.app_state.add_status(message)
            self._refresh_all_views()
            return message
        model_name = self._style_image_model_var.get().strip() or None
        use_vlm = self._use_vision_var.get()
        result = self.image_style_orchestrator.extract_style(
            image_path=image_path,
            style_name=None,
            use_vlm=use_vlm,
            vlm_model=model_name,
        )
        self.app_state.set_selected_style_image_path(image_path)
        self.app_state.set_style_extraction_result(result)
        if result.success and result.style_profile is not None:
            self.app_state.add_status(
                f"Extracted style draft: {result.style_profile.style_name}"
            )
        else:
            self.app_state.add_status("Style extraction failed.")
        self._refresh_all_views()
        if result.success and result.style_profile is not None:
            return f"Extracted style draft: {result.style_profile.style_name}"
        return "; ".join(result.errors) if result.errors else "Style extraction failed."

    def save_extracted_style_action(self) -> str:
        result = self.app_state.last_style_extraction_result
        if result is None or result.style_profile is None:
            message = "Extract a style from an image first."
            self.app_state.add_status(message)
            self._refresh_all_views()
            return message
        style = result.style_profile
        style_name = simpledialog.askstring(
            "Save Extracted Style",
            "Style name:",
            initialvalue=style.style_name,
        )
        if not style_name:
            return "Style save cancelled."
        style.metadata.style_name = style_name
        style.metadata.style_id = self.style_store._safe_name(style_name)
        path = self.style_manager.save_extracted_style(style)
        self.app_state.set_active_style_profile(style)
        if hasattr(self, "_style_var"):
            self._style_var.set(style.style_name)
        self.app_state.add_status(f"Extracted style saved: {path}")
        self._refresh_available_styles()
        self._refresh_all_views()
        return f"Extracted style saved: {path}"

    def apply_extracted_style_action(self) -> str:
        result = self.app_state.last_style_extraction_result
        if result is None or result.style_profile is None:
            message = "Extract a style from an image first."
            self.app_state.add_status(message)
            self._refresh_all_views()
            return message
        if self.app_state.current_visual_plan is None:
            message = "Create a visual plan before applying an extracted style."
            self.app_state.add_status(message)
            self._refresh_all_views()
            return message
        style = result.style_profile
        application_result = self.style_applier.apply_style(
            self.app_state.current_visual_plan, style
        )
        self.app_state.apply_style_to_current_plan(application_result)
        if not application_result.success or application_result.visual_plan is None:
            message = (
                "; ".join(application_result.errors)
                if application_result.errors
                else "Extracted style application failed."
            )
            self.app_state.add_status(message)
            self._refresh_all_views()
            return message
        self.app_state.set_active_style_profile(style)
        if hasattr(self, "_style_var"):
            self._style_var.set(style.style_name)
        self.app_state.add_status(f"Applied extracted style: {style.style_name}")
        self._refresh_all_views()
        return f"Applied extracted style: {style.style_name}"

    def _looks_like_process_request(self, content: str) -> bool:
        text = content.lower()
        return "flowchart" in text or "process" in text or "diagram" in text

    def _selected_style_profile(self):
        selected = self._style_var.get().strip()
        if not selected:
            return self.app_state.active_style_profile
        for style in self.app_state.available_style_profiles:
            if style.style_name == selected or style.style_id == selected:
                return style
        return self.style_manager.get_style_by_id(selected)

    def _style_profile_from_plan(self):
        plan = self.app_state.current_visual_plan
        if plan is None:
            return None
        from semantic_visual_builder.styles.style_schema import (
            ChartStyle,
            ColourPalette,
            DiagramStyle,
            RendererStyleHints,
            StyleMetadata,
            StyleProfile,
            TypographyStyle,
        )

        style_id = plan.metadata.style_profile_id or "current_plan_style"
        style_name = (
            plan.metadata.style_profile_name or plan.style.title or "Current Style"
        )
        return StyleProfile(
            metadata=StyleMetadata(
                style_id=style_id,
                style_name=style_name,
                description=("Derived from current visual plan."),
            ),
            palette=ColourPalette(
                primary=plan.style.palette.get("primary"),
                secondary=plan.style.palette.get("secondary"),
                accent=plan.style.palette.get("accent"),
                neutral=plan.style.palette.get("neutral"),
                warning=plan.style.palette.get("warning"),
                success=plan.style.palette.get("success"),
                danger=plan.style.palette.get("danger"),
                sequence=[
                    value
                    for key, value in plan.style.palette.items()
                    if key.startswith("sequence_")
                ],
            ),
            typography=TypographyStyle(font_family=plan.style.font_family),
            chart=ChartStyle(
                background=plan.style.background,
                plot_background=plan.style.plot_background,
                grid=plan.style.grid,
                legend_position=plan.style.legend_position,
                label_density="medium",
                title_alignment="left",
            ),
            diagram=DiagramStyle(direction=plan.style.diagram_direction),
            renderer_hints=RendererStyleHints(),
        )

    def workflow_step_text(self) -> str:
        return f"Workflow step: {self.app_state.workflow_state.current_step.value}"

    def visual_plan_text(self) -> str:
        plan = self.app_state.current_visual_plan
        return (
            summarize_visual_plan(plan) if plan is not None else "No visual plan yet."
        )

    def validation_text_value(self) -> str:
        return self._format_validation(self.app_state.current_validation_result)

    def revision_count_text(self) -> str:
        return f"Revision count: {self.app_state.revision_history.count()}"

    def run(self) -> None:
        self.root.mainloop()


class TkinterApp:
    """Stub for the future desktop UI."""

    def run(self) -> None:
        """Placeholder run method."""
        return None
