"""Embedded preview surface tests."""


from semantic_visual_builder.webview.embedded_preview import (
    BrowserPreviewSurface,
    EmbeddedWebViewPreviewSurface,
)


def test_browser_preview_surface_can_be_called_with_mocked_webbrowser(monkeypatch, tmp_path) -> None:
    calls = []
    monkeypatch.setattr("semantic_visual_builder.webview.embedded_preview.webbrowser.open", lambda uri: calls.append(uri))
    path = tmp_path / "preview.html"
    path.write_text("<html></html>", encoding="utf-8")
    BrowserPreviewSurface().show_html_file(path)
    assert calls and calls[0].startswith("file:")


def test_embedded_preview_stub_does_not_break_imports(monkeypatch, tmp_path) -> None:
    calls = []
    monkeypatch.setattr("semantic_visual_builder.webview.embedded_preview.webbrowser.open", lambda uri: calls.append(uri))
    path = tmp_path / "preview.html"
    path.write_text("<html></html>", encoding="utf-8")
    EmbeddedWebViewPreviewSurface().show_html_file(path)
    assert calls and calls[0].startswith("file:")
    assert path.exists()
