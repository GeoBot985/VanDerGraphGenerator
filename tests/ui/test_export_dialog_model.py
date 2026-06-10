"""Tests for ExportDialogController."""

from __future__ import annotations

from pathlib import Path

import pytest

from semantic_visual_builder.export.export_manager import ExportRequest
from semantic_visual_builder.ui.export_dialog import ExportDialogController


@pytest.fixture()
def ctrl() -> ExportDialogController:
    return ExportDialogController()


class TestExportDialogController:
    def test_validate_valid_html(self, ctrl: ExportDialogController, tmp_path: Path) -> None:
        errors = ctrl.validate_request("html", str(tmp_path))
        assert errors == []

    def test_validate_unknown_type(self, ctrl: ExportDialogController, tmp_path: Path) -> None:
        errors = ctrl.validate_request("docx", str(tmp_path))
        assert len(errors) == 1
        assert "Unsupported" in errors[0]

    def test_validate_empty_dir(self, ctrl: ExportDialogController) -> None:
        errors = ctrl.validate_request("html", "")
        assert any("directory" in e.lower() for e in errors)

    def test_report_html_requires_title(self, ctrl: ExportDialogController, tmp_path: Path) -> None:
        errors = ctrl.validate_request("report_html", str(tmp_path), title="")
        assert any("title" in e.lower() for e in errors)

    def test_report_html_with_title_passes(self, ctrl: ExportDialogController, tmp_path: Path) -> None:
        errors = ctrl.validate_request("report_html", str(tmp_path), title="My Report")
        assert errors == []

    def test_submit_html_creates_file(self, ctrl: ExportDialogController, tmp_path: Path) -> None:
        req = ExportRequest(export_type="html", export_dir=tmp_path, content="<p>test</p>")
        result = ctrl.submit(req)
        assert result.success is True

    def test_last_result_after_submit(self, ctrl: ExportDialogController, tmp_path: Path) -> None:
        req = ExportRequest(export_type="html", export_dir=tmp_path, content="<p>x</p>")
        ctrl.submit(req)
        assert ctrl.last_result() is not None

    def test_status_text_no_export(self, ctrl: ExportDialogController) -> None:
        assert "No export yet" in ctrl.status_text()

    def test_status_text_after_success(self, ctrl: ExportDialogController, tmp_path: Path) -> None:
        req = ExportRequest(export_type="html", export_dir=tmp_path, content="<p>x</p>")
        ctrl.submit(req)
        assert "Exported" in ctrl.status_text()

    def test_supported_types_text_has_all_types(self, ctrl: ExportDialogController) -> None:
        text = ctrl.supported_types_text()
        for t in ("html", "report_html", "png", "svg"):
            assert t in text
