"""Tests for ExportManager."""

from __future__ import annotations

from pathlib import Path

import pytest

from semantic_visual_builder.export.export_manager import ExportManager, ExportRequest


@pytest.fixture()
def export_dir(tmp_path: Path) -> Path:
    return tmp_path / "exports"


class TestExportRequest:
    def test_valid_html_type(self, export_dir: Path) -> None:
        req = ExportRequest(export_type="html", export_dir=export_dir, content="<p>test</p>")
        assert req.export_type == "html"

    def test_valid_report_html_type(self, export_dir: Path) -> None:
        req = ExportRequest(export_type="report_html", export_dir=export_dir, content="<p>test</p>")
        assert req.export_type == "report_html"

    def test_invalid_type_raises(self, export_dir: Path) -> None:
        with pytest.raises(ValueError, match="Unknown export_type"):
            ExportRequest(export_type="docx", export_dir=export_dir)


class TestExportManager:
    def test_html_export_creates_file(self, export_dir: Path) -> None:
        req = ExportRequest(export_type="html", export_dir=export_dir, content="<p>hello</p>")
        result = ExportManager().export(req)
        assert result.success is True
        assert result.path is not None
        assert result.path.exists()

    def test_report_html_export_succeeds(self, export_dir: Path) -> None:
        req = ExportRequest(
            export_type="report_html",
            export_dir=export_dir,
            content="<div>chart</div>",
            title="Sprint 12 Report",
        )
        result = ExportManager().export(req)
        assert result.success is True
        assert result.export_type == "report_html"

    def test_report_html_title_in_file(self, export_dir: Path) -> None:
        req = ExportRequest(
            export_type="report_html",
            export_dir=export_dir,
            content="<div>x</div>",
            title="My Title",
        )
        result = ExportManager().export(req)
        content = result.path.read_text(encoding="utf-8")
        assert "My Title" in content

    def test_filename_prefix_used(self, export_dir: Path) -> None:
        req = ExportRequest(
            export_type="html",
            export_dir=export_dir,
            content="<p>hi</p>",
            filename_prefix="sprint12",
        )
        result = ExportManager().export(req)
        assert "sprint12" in result.path.name
