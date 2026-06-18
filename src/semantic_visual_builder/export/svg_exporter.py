"""SVG export via headless Chromium (Playwright)."""

from __future__ import annotations

from pathlib import Path

from .export_result import ExportResult


class SvgExporter:
    """Extract the rendered chart SVG from chart HTML via headless Chromium.

    Falls back to a graceful failure message if Playwright or a Chromium
    browser binary is unavailable, or if no <svg> node is present.
    """

    def __init__(self, export_dir: Path | None = None) -> None:
        self.export_dir = export_dir

    def export_svg(
        self,
        source_html_path: Path | str | None = None,
        html: str | None = None,
        filename_prefix: str = "export",
    ) -> ExportResult:
        if source_html_path is None:
            return ExportResult(
                success=False,
                export_type="svg",
                error="A source HTML path is required for SVG export.",
            )
        from .playwright_exporter import PlaywrightExporter

        target_dir = self.export_dir if self.export_dir is not None else Path.cwd()
        return PlaywrightExporter().export_svg(
            source_html_path=Path(source_html_path),
            export_dir=Path(target_dir),
            filename_prefix=filename_prefix,
        )
