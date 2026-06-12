"""Logic-only controller for the export dialog UI."""

from __future__ import annotations

from dataclasses import dataclass, field

from semantic_visual_builder.export.export_manager import ExportManager, ExportRequest
from semantic_visual_builder.export.export_result import ExportResult

_SUPPORTED_TYPES = {"html", "report_html", "png", "svg"}


@dataclass
class ExportDialogController:
    """Validates and submits an export request without any Tkinter dependency."""

    export_manager: ExportManager = field(default_factory=ExportManager)
    _last_result: ExportResult | None = None

    def validate_request(
        self,
        export_type: str,
        export_dir: str,
        title: str = "",
    ) -> list[str]:
        errors: list[str] = []
        if export_type not in _SUPPORTED_TYPES:
            errors.append(f"Unsupported export type: {export_type!r}. Choose from: {', '.join(sorted(_SUPPORTED_TYPES))}")
        if not export_dir or not export_dir.strip():
            errors.append("Export directory must not be empty.")
        if not title.strip() and export_type == "report_html":
            errors.append("Title is required for report HTML export.")
        return errors

    def submit(self, request: ExportRequest) -> ExportResult:
        self._last_result = self.export_manager.export(request)
        return self._last_result

    def last_result(self) -> ExportResult | None:
        return self._last_result

    def status_text(self) -> str:
        if self._last_result is None:
            return "No export yet."
        if self._last_result.success:
            path = self._last_result.path
            return f"Exported: {path.name if path else '(unknown)'}"
        return f"Export failed: {self._last_result.error or 'unknown error'}"

    def supported_types_text(self) -> str:
        descriptions = {
            "html": "HTML (raw preview)",
            "report_html": "HTML Report (titled, self-contained)",
            "png": "PNG image",
            "svg": "SVG vector image",
        }
        return "\n".join(f"  {k}: {v}" for k, v in sorted(descriptions.items()))
