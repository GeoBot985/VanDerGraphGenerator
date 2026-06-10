"""Tkinter desktop shell."""

from __future__ import annotations

from pathlib import Path
import tkinter as tk
from tkinter import filedialog, ttk

from semantic_visual_builder.data.csv_loader import CsvLoader
from semantic_visual_builder.data.data_profiler import DataProfiler
from semantic_visual_builder.knowledge.capability_answerer import CapabilityAnswerer
from semantic_visual_builder.planning.field_mapper import FieldMapper
from semantic_visual_builder.planning.intent_mapper import IntentMapper
from semantic_visual_builder.planning.message_classifier import MessageClassifier, MessageIntent
from semantic_visual_builder.planning.refinement_engine import RefinementEngine
from semantic_visual_builder.planning.visual_plan import summarize_visual_plan
from semantic_visual_builder.planning.workflow_state import WorkflowStep
from semantic_visual_builder.state.app_state import AppState
from semantic_visual_builder.ui.widgets import make_readonly_text, set_text
from semantic_visual_builder.validation.capability_validator import CapabilityValidator
from semantic_visual_builder.validation.visual_plan_validator import VisualPlanValidator


class SemanticVisualBuilderApp:
    """Minimal Tkinter shell for guided semantic visual planning."""

    def __init__(self, app_state: AppState, root: tk.Misc | None = None, build_ui: bool = True):
        self.app_state = app_state
        self.csv_loader = CsvLoader()
        self.data_profiler = DataProfiler()
        self.message_classifier = MessageClassifier()
        self.intent_mapper = IntentMapper()
        self.field_mapper = FieldMapper()
        self.refinement_engine = RefinementEngine()
        self.plan_validator = VisualPlanValidator()
        self.capability_validator = CapabilityValidator()
        self.capability_answerer = CapabilityAnswerer(app_state.product_kb) if app_state.product_kb else None
        self.conversation_state = self.app_state.conversation_state
        self.root = root or (tk.Tk() if build_ui else None)
        if self.root is None:
            return
        self.root.title("Van Der Graph Generator")
        self.root.geometry("1100x760")
        self._model_var = tk.StringVar(value="")
        self._status_var = tk.StringVar(value="")
        self._chat_var = tk.StringVar(value="")
        self._workflow_var = tk.StringVar(value="")
        self._revision_var = tk.StringVar(value="")
        self._build_ui()
        self.refresh_ollama()
        self._refresh_all_views()

    def _build_ui(self) -> None:
        header = ttk.Label(self.root, text="Van Der Graph Generator", font=("Segoe UI", 18, "bold"))
        header.pack(anchor="w", padx=12, pady=(12, 6))

        top = ttk.Frame(self.root)
        top.pack(fill="x", padx=12)
        self.status_label = ttk.Label(top, textvariable=self._status_var)
        self.status_label.pack(side="left")
        ttk.Label(top, text="Model:").pack(side="left", padx=(24, 6))
        self.model_combo = ttk.Combobox(top, textvariable=self._model_var, state="readonly", width=34)
        self.model_combo.pack(side="left")
        ttk.Button(top, text="Refresh Models", command=self.refresh_ollama).pack(side="left", padx=6)
        ttk.Button(top, text="Load CSV", command=self.load_csv).pack(side="left", padx=6)

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
        ttk.Button(entry_row, text="Send", command=self.send_chat).pack(side="left", padx=6)

        ttk.Label(right, text="Preview").pack(anchor="w")
        self.preview_text = make_readonly_text(right, height=4)
        self.preview_text.pack(fill="both", expand=False, pady=(4, 8))

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

    def refresh_ollama(self) -> None:
        from semantic_visual_builder.llm.ollama_client import OllamaClient

        client = OllamaClient()
        status = client.get_status()
        models = client.list_models() if status.is_connected else []
        self.app_state.ollama_status = status
        self.app_state.model_registry.set_models(models)
        self._model_var.set(self.app_state.model_registry.selected_model or "")
        self.model_combo["values"] = self.app_state.model_registry.get_model_names()
        if status.is_connected:
            self._set_status("Ollama connected.")
        else:
            self._set_status("Ollama not connected. Start Ollama and click Refresh Models.")
        self._refresh_all_views()

    def load_csv(self) -> None:
        filename = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if not filename:
            return
        loaded = self.csv_loader.load(path=Path(filename))
        profile = self.data_profiler.profile(loaded.dataframe)
        self.app_state.dataset_context.loaded_dataset = loaded
        self.app_state.dataset_context.profile = profile
        self.app_state.current_visual_plan = None
        self.app_state.current_validation_result = None
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

        intent = self.message_classifier.classify(content, has_current_plan=self.app_state.current_visual_plan is not None)
        if intent == MessageIntent.CAPABILITY_QUESTION:
            response = self._answer_capability_question(content)
        elif intent == MessageIntent.WORKFLOW_HELP:
            response = self._workflow_help_text()
        elif intent == MessageIntent.VISUAL_REQUEST:
            response = self._handle_visual_request(content)
        elif intent == MessageIntent.REFINEMENT_REQUEST:
            response = self._handle_refinement_request(content)
        else:
            response = "Please load data, ask about capabilities, or describe the visual goal."
        self._append_assistant_response(response)
        self._refresh_all_views()

    def _answer_capability_question(self, question: str) -> str:
        if self.capability_answerer is None:
            return "Capability answers are unavailable until the product knowledge base loads."
        answer = self.capability_answerer.answer(question)
        self.app_state.add_status("Answered capability question from Product KB.")
        return answer

    def _workflow_help_text(self) -> str:
        workflow = self.app_state.product_kb.workflow.get("workflow", []) if self.app_state.product_kb else []
        if not workflow:
            return "Load data, describe the visual goal, confirm the plan, then refine it."
        lines = ["Guided workflow:"]
        for step in workflow:
            if isinstance(step, dict):
                lines.append(f"{step.get('step')}. {step.get('name')}: {step.get('description')}")
        self.app_state.add_status("Displayed workflow guidance.")
        return "\n".join(lines)

    def _handle_visual_request(self, content: str) -> str:
        dataset_profile = self.app_state.dataset_context.profile
        if dataset_profile is None and not self._looks_like_process_request(content):
            self.app_state.workflow_state.advance_to(WorkflowStep.DATA_REQUIRED)
            return "Please load a dataset first so I can map the visual request deterministically."

        plan = self.intent_mapper.map_request_to_plan(content, dataset_profile, self.app_state.graph_matrix)
        if dataset_profile is not None:
            plan = self.field_mapper.propose_roles(content, dataset_profile, plan)

        validation = self.plan_validator.validate(plan, dataset_profile, self.app_state.graph_matrix)
        capability_check = self.capability_validator.validate_against_capabilities(plan, self.app_state.product_kb) if self.app_state.product_kb else None
        if capability_check is not None:
            for message in capability_check.messages:
                validation.messages.append(message)
        self.app_state.set_visual_plan(plan, description="Created visual plan")
        self.app_state.set_validation_result(validation)

        if validation.is_valid:
            self.app_state.workflow_state.advance_to(WorkflowStep.PLAN_READY)
            self.app_state.add_status("Created and validated a neutral visual plan.")
        else:
            self.app_state.workflow_state.advance_to(WorkflowStep.FIELD_MAPPING_CONFIRMED)
            self.app_state.add_status("Visual plan created with validation issues.")
        return self._visual_plan_response(plan, validation)

    def _handle_refinement_request(self, content: str) -> str:
        if self.app_state.current_visual_plan is None:
            return "Create a visual plan first, then I can apply refinements."
        refined = self.refinement_engine.apply_refinement(self.app_state.current_visual_plan, content)
        validation = self.plan_validator.validate(refined, self.app_state.dataset_context.profile, self.app_state.graph_matrix)
        if self.app_state.product_kb is not None:
            capability_check = self.capability_validator.validate_against_capabilities(refined, self.app_state.product_kb)
            validation.messages.extend(capability_check.messages)
        self.app_state.set_visual_plan(refined, description="Refined visual plan")
        self.app_state.set_validation_result(validation)
        self.app_state.workflow_state.advance_to(WorkflowStep.REFINEMENT_LOOP)
        self.app_state.add_status("Applied refinement to the current visual plan.")
        return self._visual_plan_response(refined, validation)

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
            lines.append(
                f"{column.name} | {column.dtype} | {column.semantic_type} | nulls={column.null_count} | uniques={column.unique_count}"
            )
        set_text(self.profile_text, "\n".join(lines))

    def _update_plan_view(self) -> None:
        plan = self.app_state.current_visual_plan
        set_text(self.plan_text, summarize_visual_plan(plan) if plan is not None else "No visual plan yet.")

    def _update_validation_view(self) -> None:
        validation = self.app_state.current_validation_result
        set_text(self.validation_text, self._format_validation(validation) if validation is not None else "No validation result yet.")

    def _update_workflow_view(self) -> None:
        self._workflow_var.set(f"Workflow step: {self.app_state.workflow_state.current_step.value}")
        self._revision_var.set(f"Revision count: {self.app_state.revision_history.count()}")

    def _refresh_debug(self) -> None:
        lines = list(self.app_state.status_messages)
        if self.app_state.ollama_status:
            lines.append(f"Ollama connected: {self.app_state.ollama_status.is_connected}")
            if self.app_state.ollama_status.version:
                lines.append(f"Ollama version: {self.app_state.ollama_status.version}")
            if self.app_state.ollama_status.error:
                lines.append(f"Ollama error: {self.app_state.ollama_status.error}")
        set_text(self.debug_text, "\n".join(lines) or "Ready.")

    def _refresh_all_views(self) -> None:
        if self.root is None:
            return
        self._update_profile_view()
        self._update_plan_view()
        self._update_validation_view()
        self._update_workflow_view()
        self._refresh_debug()

    def _set_status(self, message: str) -> None:
        self._status_var.set(message)
        self.app_state.add_status(message)
        self._refresh_debug()

    def _format_validation(self, validation) -> str:
        if validation is None:
            return "No validation result yet."
        if not validation.messages:
            return "Plan is valid."
        return "\n".join(f"{item.severity.value.upper()}: {item.message}" for item in validation.messages)

    def _looks_like_process_request(self, content: str) -> bool:
        text = content.lower()
        return "flowchart" in text or "process" in text or "diagram" in text

    def workflow_step_text(self) -> str:
        return f"Workflow step: {self.app_state.workflow_state.current_step.value}"

    def visual_plan_text(self) -> str:
        plan = self.app_state.current_visual_plan
        return summarize_visual_plan(plan) if plan is not None else "No visual plan yet."

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
