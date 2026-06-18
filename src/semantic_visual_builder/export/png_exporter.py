"""PNG export via headless Chromium (Playwright)."""

from __future__ import annotations

from pathlib import Path

from .export_result import ExportResult


class PngExporter:
    """Render chart HTML to a PNG via headless Chromium.

    Falls back to a graceful failure message if Playwright or a Chromium
    browser binary is unavailable.
    """

    def __init__(self, export_dir: Path | None = None) -> None:
        self.export_dir = export_dir

    def export_png(
        self,
        source_html_path: Path | str | None = None,
        html: str | None = None,
        filename_prefix: str = "export",
    ) -> ExportResult:
        if source_html_path is None:
            return ExportResult(
                success=False,
                export_type="png",
                error="A source HTML path is required for PNG export.",
            )
        from .playwright_exporter import PlaywrightExporter

        target_dir = self.export_dir if self.export_dir is not None else Path.cwd()
        return PlaywrightExporter().export_png(
            source_html_path=Path(source_html_path),
            export_dir=Path(target_dir),
            filename_prefix=filename_prefix,
        )
