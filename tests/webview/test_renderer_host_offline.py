"""Renderer host offline tests."""

from pathlib import Path

from semantic_visual_builder.renderers.renderer_result import RendererOutput
from semantic_visual_builder.webview.asset_manager import AssetManager
from semantic_visual_builder.webview.renderer_host import RendererHost


def test_plotly_template_uses_local_asset_when_present(tmp_path) -> None:
    template_dir = Path(__file__).resolve().parents[2] / "src" / "semantic_visual_builder" / "webview" / "templates"
    vendor = tmp_path / "vendor"
    asset_path = vendor / "plotly" / "plotly.min.js"
    asset_path.parent.mkdir(parents=True)
    asset_path.write_text("console.log('plotly');", encoding="utf-8")
    host = RendererHost(template_dir, AssetManager(vendor))
    result = host.build_html(RendererOutput(renderer_name="plotly", output_type="plotly_json", content='{"data": [], "layout": {}}'))
    assert asset_path.resolve().as_uri() in result.html
    assert not result.warnings
    assert "{{" not in result.html


def test_mermaid_template_uses_local_asset_when_present(tmp_path) -> None:
    template_dir = Path(__file__).resolve().parents[2] / "src" / "semantic_visual_builder" / "webview" / "templates"
    vendor = tmp_path / "vendor"
    asset_path = vendor / "mermaid" / "mermaid.min.js"
    asset_path.parent.mkdir(parents=True)
    asset_path.write_text("console.log('mermaid');", encoding="utf-8")
    host = RendererHost(template_dir, AssetManager(vendor))
    result = host.build_html(RendererOutput(renderer_name="mermaid", output_type="mermaid", content="flowchart TD\nA-->B"))
    assert asset_path.resolve().as_uri() in result.html
    assert "{{" not in result.html


def test_cdn_fallback_warning_appears_when_missing(tmp_path) -> None:
    template_dir = Path(__file__).resolve().parents[2] / "src" / "semantic_visual_builder" / "webview" / "templates"
    host = RendererHost(template_dir, AssetManager(tmp_path / "vendor"))
    result = host.build_html(RendererOutput(renderer_name="plotly", output_type="plotly_json", content='{"data": [], "layout": {}}'))
    assert result.warnings
    assert "CDN fallback" in result.warnings[0]


def test_no_unresolved_placeholders_remain(tmp_path) -> None:
    template_dir = Path(__file__).resolve().parents[2] / "src" / "semantic_visual_builder" / "webview" / "templates"
    host = RendererHost(template_dir, AssetManager(tmp_path / "vendor"))
    result = host.build_html(RendererOutput(renderer_name="chartjs", output_type="chartjs_json", content='{"type": "bar"}'))
    assert "{{" not in result.html
