"""PNG exporter placeholder for future work.

The current implementation is a graceful stub. A future sprint can replace the
body with a headless-browser render path (e.g. Playwright) that converts the
generated chart HTML into a PNG image.
"""

from __future__ import annotations

from pathlib import Path

from .export_result import ExportResult


class PngExporter:
    """Graceful stub for browser-rendered PNG export."""

    def __init__(self, export_dir: Path | None = None) -> None:
        self.export_dir = export_dir

    def export_png(
        self,
        source_html_path: Path | str | None = None,
        html: str | None = None,
        filename_prefix: str = "export",
    ) -> ExportResult:
        return ExportResult(
            success=False,
            export_type="png",
            error=(
                "PNG export is not yet implemented. Use the browser's "
                "save-as-image option on the preview, or wait for the "
                "headless-renderer export path in a later sprint."
            ),
        )
