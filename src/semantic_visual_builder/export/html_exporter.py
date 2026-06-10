"""Write preview HTML to disk."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from semantic_visual_builder.utils.file_utils import ensure_parent_dir
from semantic_visual_builder.utils.text_sanitize import normalize_name

from .export_result import ExportResult


class HtmlExporter:
    """Export HTML previews to timestamped files."""

    def __init__(self, export_dir: Path):
        self.export_dir = export_dir

    def export_html(self, html: str, filename_prefix: str = "preview") -> ExportResult:
        try:
            self.export_dir.mkdir(parents=True, exist_ok=True)
            timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
            safe_prefix = normalize_name(filename_prefix) or "preview"
            path = self.export_dir / f"{safe_prefix}_{timestamp}.html"
            ensure_parent_dir(path)
            path.write_text(html, encoding="utf-8")
            return ExportResult(success=True, path=path, export_type="html")
        except Exception as exc:
            return ExportResult(success=False, export_type="html", error=str(exc))
