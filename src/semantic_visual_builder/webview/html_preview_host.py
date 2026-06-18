"""Open preview HTML files in the default browser."""

from __future__ import annotations

from pathlib import Path

from .embedded_preview import BrowserPreviewSurface, PreviewSurface


class HtmlPreviewHost:
    """Open preview pages using the standard library browser module."""

    def __init__(self, preview_surface: PreviewSurface | None = None):
        self.preview_surface = preview_surface or BrowserPreviewSurface()

    def open_preview(self, html_path: Path) -> None:
        self.preview_surface.show_html_file(html_path)
