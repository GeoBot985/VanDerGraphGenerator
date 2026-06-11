"""UI widget helpers."""

from __future__ import annotations

import tkinter as tk
from collections.abc import Callable


class HoverTooltip:
    """Simple hover tooltip for Tk widgets."""

    def __init__(
        self,
        widget: tk.Widget,
        text: str | Callable[[], str],
        *,
        wraplength: int = 420,
    ) -> None:
        self.widget = widget
        self.text = text
        self.wraplength = wraplength
        self._tooltip_window: tk.Toplevel | None = None
        self.widget.bind("<Enter>", self._show, add="+")
        self.widget.bind("<Leave>", self._hide, add="+")
        self.widget.bind("<ButtonPress>", self._hide, add="+")

    def _resolve_text(self) -> str:
        if callable(self.text):
            return self.text()
        return self.text

    def _show(self, event: tk.Event | None = None) -> None:
        _ = event
        if self._tooltip_window is not None:
            return
        content = self._resolve_text().strip()
        if not content:
            return
        x = self.widget.winfo_rootx() + 18
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 8
        self._tooltip_window = tk.Toplevel(self.widget)
        self._tooltip_window.wm_overrideredirect(True)
        self._tooltip_window.wm_geometry(f"+{x}+{y}")
        label = tk.Label(
            self._tooltip_window,
            text=content,
            justify="left",
            background="#fff9e8",
            foreground="#2b2418",
            relief="solid",
            borderwidth=1,
            padx=10,
            pady=8,
            wraplength=self.wraplength,
            font=("Segoe UI", 9),
        )
        label.pack()

    def _hide(self, event: tk.Event | None = None) -> None:
        _ = event
        if self._tooltip_window is not None:
            self._tooltip_window.destroy()
            self._tooltip_window = None


def make_readonly_text(parent: tk.Widget, height: int = 8) -> tk.Text:
    text = tk.Text(
        parent,
        height=height,
        wrap="word",
        padx=10,
        pady=8,
        relief="solid",
        borderwidth=1,
    )
    text.configure(state="disabled")
    return text


def set_text(widget: tk.Text, content: str) -> None:
    widget.configure(state="normal")
    widget.delete("1.0", tk.END)
    widget.insert("1.0", content)
    widget.configure(state="disabled")
