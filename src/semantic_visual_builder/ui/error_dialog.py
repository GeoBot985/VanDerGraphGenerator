"""User-friendly error dialog helpers."""

from __future__ import annotations

from tkinter import messagebox


def show_error_dialog(title: str, message: str, details: str | None = None, parent=None) -> None:
    text = message if details is None else f"{message}\n\nDetails:\n{details}"
    messagebox.showerror(title, text, parent=parent)
