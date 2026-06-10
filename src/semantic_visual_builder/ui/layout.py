"""UI layout helpers."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk


def build_main_layout(parent: tk.Widget) -> dict[str, tk.Widget]:
    """Build the Sprint 1 layout and return key widgets."""

    header = ttk.Label(parent, text="Van Der Graph Generator", font=("Segoe UI", 16, "bold"))
    header.pack(anchor="w", padx=12, pady=(12, 4))
    return {"header": header}
