"""Tests for ReportHtmlExporter."""

from __future__ import annotations

from pathlib import Path

import pytest

from semantic_visual_builder.export.report_html_exporter import ReportHtmlExporter


@pytest.fixture()
def exporter(tmp_path: Path) -> ReportHtmlExporter:
    return ReportHtmlExporter(tmp_path / "reports")


CHART_HTML = "<div id='chart'>chart content here</div>"


class TestReportHtmlExporter:
    def test_creates_file(self, exporter: ReportHtmlExporter) -> None:
        result = exporter.export_report(CHART_HTML, title="Test Report")
        assert result.success is True
        assert result.path is not None
        assert result.path.exists()

    def test_export_type_is_report_html(self, exporter: ReportHtmlExporter) -> None:
        result = exporter.export_report(CHART_HTML)
        assert result.export_type == "report_html"

    def test_title_in_output(self, exporter: ReportHtmlExporter) -> None:
        result = exporter.export_report(CHART_HTML, title="My Report")
        content = result.path.read_text(encoding="utf-8")
        assert "My Report" in content

    def test_chart_html_embedded(self, exporter: ReportHtmlExporter) -> None:
        result = exporter.export_report(CHART_HTML)
        content = result.path.read_text(encoding="utf-8")
        assert "chart content here" in content

    def test_renderer_name_in_output(self, exporter: ReportHtmlExporter) -> None:
        result = exporter.export_report(CHART_HTML, renderer_name="plotly")
        content = result.path.read_text(encoding="utf-8")
        assert "plotly" in content

    def test_notes_in_output(self, exporter: ReportHtmlExporter) -> None:
        result = exporter.export_report(CHART_HTML, notes="Q4 review data")
        content = result.path.read_text(encoding="utf-8")
        assert "Q4 review data" in content

    def test_html_is_valid_doctype(self, exporter: ReportHtmlExporter) -> None:
        result = exporter.export_report(CHART_HTML)
        content = result.path.read_text(encoding="utf-8")
        assert content.strip().startswith("<!DOCTYPE html>")

    def test_title_xss_escaped(self, exporter: ReportHtmlExporter) -> None:
        result = exporter.export_report(CHART_HTML, title="<script>alert(1)</script>")
        content = result.path.read_text(encoding="utf-8")
        assert "<script>" not in content

    def test_failure_returns_error_result(self, tmp_path: Path) -> None:
        # Use a filename with null bytes which is always invalid on any OS
        bad_path = tmp_path / "ok"
        exporter = ReportHtmlExporter(bad_path)

        # Monkey-patch write_text to force a failure
        def _raise(*args, **kwargs):
            raise OSError("forced failure")

        import unittest.mock as mock
        with mock.patch.object(Path, "write_text", _raise):
            result = exporter.export_report(CHART_HTML)
        assert result.success is False
        assert result.error is not None
