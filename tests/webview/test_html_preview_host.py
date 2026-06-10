"""HTML preview host tests."""

from pathlib import Path

from semantic_visual_builder.renderers.renderer_result import RendererOutput
from semantic_visual_builder.webview.html_preview_host import HtmlPreviewHost
from semantic_visual_builder.webview.renderer_host import RendererHost


def test_renderer_host_builds_plotly_html_without_placeholders() -> None:
    host = RendererHost(Path(__file__).resolve().parents[2] / "src" / "semantic_visual_builder" / "webview" / "templates")
    html = host.build_html(RendererOutput(renderer_name="plotly", output_type="plotly_json", content='{"data": [], "layout": {}}'))
    assert "{{PLOTLY_CONFIG_JSON}}" not in html
    assert "Plotly.newPlot" in html


def test_renderer_host_builds_mermaid_html_without_placeholders() -> None:
    host = RendererHost(Path(__file__).resolve().parents[2] / "src" / "semantic_visual_builder" / "webview" / "templates")
    html = host.build_html(RendererOutput(renderer_name="mermaid", output_type="mermaid", content="flowchart TD\n    A --> B"))
    assert "{{MERMAID_CODE}}" not in html
    assert "mermaid.initialize" in html


def test_html_preview_host_opens_browser_with_file_uri(monkeypatch, tmp_path) -> None:
    calls = []

    monkeypatch.setattr("semantic_visual_builder.webview.html_preview_host.webbrowser.open", lambda uri: calls.append(uri))
    html_path = tmp_path / "preview.html"
    html_path.write_text("<html></html>", encoding="utf-8")
    HtmlPreviewHost().open_preview(html_path)
    assert calls and calls[0].startswith("file:")
