"""PNG exporter placeholder for future work."""

from __future__ import annotations

from .export_result import ExportResult


class PngExporter:
    """Graceful stub for browser-rendered PNG export."""

    def export_png(self, html: str, filename_prefix: str = "preview") -> ExportResult:
        return ExportResult(
            success=False,
            export_type="png",
            error="PNG export is not implemented in Sprint 6. Use browser save/export or a later renderer-specific static export path.",
        )
