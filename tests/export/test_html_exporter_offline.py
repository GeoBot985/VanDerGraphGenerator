"""Offline HTML exporter tests."""

from semantic_visual_builder.export.html_exporter import HtmlExporter


def test_html_export_creates_file(tmp_path) -> None:
    exporter = HtmlExporter(tmp_path / "previews")
    result = exporter.export_html("<html><body>Offline</body></html>", filename_prefix="offline")
    assert result.success is True
    assert result.path is not None and result.path.exists()


def test_invalid_export_dir_handled_clearly(monkeypatch, tmp_path) -> None:
    exporter = HtmlExporter(tmp_path / "previews")
    from pathlib import Path

    original_mkdir = Path.mkdir

    def fail_mkdir(self, *args, **kwargs):
        if self == exporter.export_dir:
            raise PermissionError("denied")
        return original_mkdir(self, *args, **kwargs)

    monkeypatch.setattr(Path, "mkdir", fail_mkdir)
    result = exporter.export_html("<html></html>")
    assert result.success is False
    assert result.error is not None
