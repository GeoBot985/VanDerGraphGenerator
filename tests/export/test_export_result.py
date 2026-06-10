"""Export result tests."""

from pathlib import Path

from semantic_visual_builder.export.export_result import ExportResult


def test_export_result_success_shape() -> None:
    result = ExportResult(success=True, path=Path("preview.html"), export_type="html")
    assert result.success is True
    assert result.path.name == "preview.html"


def test_export_result_failure_shape() -> None:
    result = ExportResult(success=False, error="boom")
    assert result.success is False
    assert result.error == "boom"
