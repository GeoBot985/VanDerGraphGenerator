"""Write preview HTML to disk."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path


class HtmlExporter:
    """Export HTML previews to timestamped files."""

    def __init__(self, export_dir: Path):
        self.export_dir = export_dir

    def export_html(self, html: str, filename_prefix: str = "preview") -> Path:
        self.export_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        path = self.export_dir / f"{filename_prefix}_{timestamp}.html"
        path.write_text(html, encoding="utf-8")
        return path
