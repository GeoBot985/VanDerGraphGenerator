"""Open preview HTML files in the default browser."""

from __future__ import annotations

import webbrowser
from pathlib import Path


class HtmlPreviewHost:
    """Open preview pages using the standard library browser module."""

    def open_preview(self, html_path: Path) -> None:
        webbrowser.open(html_path.resolve().as_uri())
