"""Export a self-contained, report-ready HTML file with title and metadata."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from .export_result import ExportResult

_HTML_TEMPLATE = """\
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{title}</title>
  <style>
    body {{ font-family: sans-serif; margin: 2rem auto; max-width: 960px; color: #222; }}
    h1 {{ font-size: 1.5rem; margin-bottom: 0.25rem; }}
    .meta {{ font-size: 0.85rem; color: #666; margin-bottom: 1.5rem; }}
    .chart-container {{ border: 1px solid #e0e0e0; border-radius: 4px; overflow: hidden; }}
    .notes {{ margin-top: 1.5rem; font-size: 0.9rem; color: #444; white-space: pre-wrap; }}
  </style>
</head>
<body>
  <h1>{title}</h1>
  <div class="meta">Generated: {generated_at}{renderer_line}{dataset_line}</div>
  <div class="chart-container">
    {chart_html}
  </div>
  {notes_block}
</body>
</html>
"""

_NOTES_BLOCK = '<div class="notes"><strong>Notes</strong>\n{notes}</div>'


class ReportHtmlExporter:
    """Wrap a renderer's HTML output in a clean report shell."""

    def __init__(self, export_dir: Path) -> None:
        self.export_dir = export_dir

    def export_report(
        self,
        chart_html: str,
        title: str = "Visual Report",
        renderer_name: str | None = None,
        dataset_name: str | None = None,
        notes: str | None = None,
        filename_prefix: str = "report",
    ) -> ExportResult:
        try:
            self.export_dir.mkdir(parents=True, exist_ok=True)
            generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
            renderer_line = f" &bull; Renderer: {renderer_name}" if renderer_name else ""
            dataset_line = f" &bull; Dataset: {dataset_name}" if dataset_name else ""
            notes_block = _NOTES_BLOCK.format(notes=notes) if notes else ""

            html = _HTML_TEMPLATE.format(
                title=_escape(title),
                generated_at=generated_at,
                renderer_line=renderer_line,
                dataset_line=_escape(dataset_name) if dataset_name else "",
                chart_html=chart_html,
                notes_block=notes_block,
            )

            timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
            safe_prefix = _safe_filename(filename_prefix) or "report"
            path = self.export_dir / f"{safe_prefix}_{timestamp}.html"
            path.write_text(html, encoding="utf-8")
            return ExportResult(success=True, path=path, export_type="report_html")
        except Exception as exc:
            return ExportResult(success=False, export_type="report_html", error=str(exc))


def _escape(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def _safe_filename(text: str) -> str:
    safe = "".join(c if c.isalnum() or c in ("-", "_") else "_" for c in text)
    return safe.strip("_")
