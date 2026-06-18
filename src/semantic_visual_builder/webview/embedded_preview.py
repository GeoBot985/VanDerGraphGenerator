"""Preview surface abstractions."""

from __future__ import annotations

import webbrowser
from abc import ABC, abstractmethod
from pathlib import Path


class PreviewSurface(ABC):
    @abstractmethod
    def show_html_file(self, html_path: Path) -> None:
        raise NotImplementedError


class BrowserPreviewSurface(PreviewSurface):
    def show_html_file(self, html_path: Path) -> None:
        webbrowser.open(html_path.resolve().as_uri())


class EmbeddedWebViewPreviewSurface(PreviewSurface):
    """Optional stub for a future embedded webview implementation."""

    def show_html_file(self, html_path: Path) -> None:
        BrowserPreviewSurface().show_html_file(html_path)
