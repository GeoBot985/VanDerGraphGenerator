"""Tkinter desktop shell."""

from __future__ import annotations

import tkinter as tk
from pathlib import Path
from tkinter import filedialog, ttk

from semantic_visual_builder.data.csv_loader import CsvLoader
from semantic_visual_builder.data.data_profiler import DataProfiler
from semantic_visual_builder.state.app_state import AppState
from semantic_visual_builder.state.conversation_state import ConversationState
from semantic_visual_builder.ui.widgets import make_readonly_text, set_text


class SemanticVisualBuilderApp:
    """Minimal Tkinter shell for Sprint 1."""

    def __init__(self, app_state: AppState, root: tk.Misc | None = None, build_ui: bool = True):
        self.app_state = app_state
        self.conversation_state = ConversationState()
        self.csv_loader = CsvLoader()
        self.data_profiler = DataProfiler()
        self.root = root or (tk.Tk() if build_ui else None)
        if self.root is None:
            return
        self.root.title("Van Der Graph Generator")
        self.root.geometry("1100x720")
        self._model_var = tk.StringVar(value="")
        self._status_var = tk.StringVar(value="")
        self._chat_var = tk.StringVar(value="")
        self._build_ui()
        self.refresh_ollama()

    def _build_ui(self) -> None:
        header = ttk.Label(self.root, text="Van Der Graph Generator", font=("Segoe UI", 18, "bold"))
        header.pack(anchor="w", padx=12, pady=(12, 6))

        top = ttk.Frame(self.root)
        top.pack(fill="x", padx=12)
        self.status_label = ttk.Label(top, textvariable=self._status_var)
        self.status_label.pack(side="left")
        ttk.Label(top, text="Model:").pack(side="left", padx=(24, 6))
        self.model_combo = ttk.Combobox(top, textvariable=self._model_var, state="readonly", width=36)
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
        self.chat_log = make_readonly_text(left, height=14)
        self.chat_log.pack(fill="both", expand=True, pady=(4, 8))
        entry_row = ttk.Frame(left)
        entry_row.pack(fill="x")
        self.chat_entry = ttk.Entry(entry_row, textvariable=self._chat_var)
        self.chat_entry.pack(side="left", fill="x", expand=True)
        ttk.Button(entry_row, text="Send", command=self.send_chat).pack(side="left", padx=6)

        ttk.Label(right, text="Preview").pack(anchor="w")
        self.preview_text = make_readonly_text(right, height=8)
        self.preview_text.pack(fill="both", expand=True, pady=(4, 8))
        ttk.Label(right, text="Dataset Profile").pack(anchor="w")
        self.profile_text = make_readonly_text(right, height=12)
        self.profile_text.pack(fill="both", expand=True, pady=(4, 0))

        ttk.Label(self.root, text="Debug / Status").pack(anchor="w", padx=12)
        self.debug_text = make_readonly_text(self.root, height=8)
        self.debug_text.pack(fill="both", expand=False, padx=12, pady=(4, 12))

        self._append_preview("Preview placeholder")
        self._refresh_debug()
        self._update_profile_view()

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
        self._refresh_debug()

    def load_csv(self) -> None:
        filename = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if not filename:
            return
        loaded = self.csv_loader.load(path=Path(filename))
        profile = self.data_profiler.profile(loaded.dataframe)
        self.app_state.dataset_context.loaded_dataset = loaded
        self.app_state.dataset_context.profile = profile
        self.app_state.add_status(f"Loaded CSV: {loaded.path.name}")
        self._update_profile_view()
        self._refresh_debug()

    def send_chat(self) -> None:
        content = self._chat_var.get().strip()
        if not content:
            return
        self.conversation_state.add_user_message(content)
        self.conversation_state.add_assistant_message("LLM interaction starts in a later sprint.")
        self._append_chat(f"User: {content}\nAssistant: LLM interaction starts in a later sprint.\n")
        self._chat_var.set("")

    def _append_chat(self, text: str) -> None:
        self.chat_log.configure(state="normal")
        self.chat_log.insert("end", text + "\n")
        self.chat_log.configure(state="disabled")

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

    def _refresh_debug(self) -> None:
        lines = list(self.app_state.status_messages)
        if self.app_state.ollama_status:
            lines.append(f"Ollama connected: {self.app_state.ollama_status.is_connected}")
            if self.app_state.ollama_status.version:
                lines.append(f"Ollama version: {self.app_state.ollama_status.version}")
            if self.app_state.ollama_status.error:
                lines.append(f"Ollama error: {self.app_state.ollama_status.error}")
        set_text(self.debug_text, "\n".join(lines) or "Ready.")

    def _set_status(self, message: str) -> None:
        self._status_var.set(message)
        self.app_state.add_status(message)
        self._refresh_debug()

    def run(self) -> None:
        self.root.mainloop()


class TkinterApp:
    """Stub for the future desktop UI."""

    def run(self) -> None:
        """Placeholder run method."""
        return None
