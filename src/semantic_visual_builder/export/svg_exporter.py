"""SVG exporter placeholder for future work."""

from __future__ import annotations

from .export_result import ExportResult


class SvgExporter:
    """Graceful stub for browser-rendered SVG export."""

    def export_svg(self, html: str, filename_prefix: str = "preview") -> ExportResult:
        return ExportResult(
            success=False,
            export_type="svg",
            error="SVG export is not implemented in Sprint 6. Use browser save/export or a later renderer-specific static export path.",
        )
