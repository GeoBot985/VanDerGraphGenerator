"""HTML exporter tests."""

from semantic_visual_builder.export.html_exporter import HtmlExporter


def test_export_directory_created_and_html_written(tmp_path) -> None:
    exporter = HtmlExporter(tmp_path / "previews")
    result = exporter.export_html("<html><body>Preview</body></html>", filename_prefix="preview")
    assert result.success is True
    assert result.path is not None
    assert result.path.exists()
    assert result.path.read_text(encoding="utf-8") == "<html><body>Preview</body></html>"
