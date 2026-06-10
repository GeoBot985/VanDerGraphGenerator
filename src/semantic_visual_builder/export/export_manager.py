"""High-level export coordinator — routes export requests to the right exporter."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from .export_result import ExportResult
from .html_exporter import HtmlExporter
from .png_exporter import PngExporter
from .report_html_exporter import ReportHtmlExporter
from .svg_exporter import SvgExporter


@dataclass
class ExportRequest:
    export_type: str
    export_dir: Path
    content: str = ""
    title: str = "Visual Report"
    renderer_name: str | None = None
    dataset_name: str | None = None
    notes: str | None = None
    filename_prefix: str = "export"
    extra: dict = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.export_type not in {"html", "report_html", "png", "svg"}:
            raise ValueError(f"Unknown export_type: {self.export_type!r}")


class ExportManager:
    """Route an ExportRequest to the appropriate exporter."""

    def export(self, request: ExportRequest) -> ExportResult:
        if request.export_type == "report_html":
            return ReportHtmlExporter(request.export_dir).export_report(
                chart_html=request.content,
                title=request.title,
                renderer_name=request.renderer_name,
                dataset_name=request.dataset_name,
                notes=request.notes,
                filename_prefix=request.filename_prefix,
            )
        if request.export_type == "html":
            return HtmlExporter(request.export_dir).export_html(
                html=request.content,
                filename_prefix=request.filename_prefix,
            )
        if request.export_type == "png":
            source_path = Path(request.extra.get("source_path", ""))
            return PngExporter(request.export_dir).export_png(
                source_html_path=source_path,
                filename_prefix=request.filename_prefix,
            )
        if request.export_type == "svg":
            source_path = Path(request.extra.get("source_path", ""))
            return SvgExporter(request.export_dir).export_svg(
                source_html_path=source_path,
                filename_prefix=request.filename_prefix,
            )
        return ExportResult(success=False, export_type=request.export_type, error="Unhandled export type")
