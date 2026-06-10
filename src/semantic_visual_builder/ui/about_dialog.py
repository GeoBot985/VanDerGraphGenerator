"""About dialog helpers."""

from __future__ import annotations

from tkinter import messagebox

from semantic_visual_builder.version import APP_NAME, INTERNAL_NAME, APP_STATUS, APP_VERSION


def show_about_dialog(parent=None) -> None:
    messagebox.showinfo(
        f"About {APP_NAME}",
        f"{APP_NAME}\n{INTERNAL_NAME}\nVersion {APP_VERSION}\n{APP_STATUS}\nLocal semantic visual-programming prototype\nLLM input ease + deterministic output reliability",
        parent=parent,
    )
