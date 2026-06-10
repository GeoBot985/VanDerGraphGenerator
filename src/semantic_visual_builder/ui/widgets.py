"""UI widget helpers."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk


def make_readonly_text(parent: tk.Widget, height: int = 8) -> tk.Text:
    text = tk.Text(parent, height=height, wrap="word")
    text.configure(state="disabled")
    return text


def set_text(widget: tk.Text, content: str) -> None:
    widget.configure(state="normal")
    widget.delete("1.0", tk.END)
    widget.insert("1.0", content)
    widget.configure(state="disabled")
