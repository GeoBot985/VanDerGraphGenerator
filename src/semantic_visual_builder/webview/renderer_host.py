"""Build standalone HTML previews from renderer output."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

from semantic_visual_builder.renderers.renderer_result import RendererOutput
from semantic_visual_builder.utils.paths import get_vendor_assets_dir

from .asset_manager import AssetManager


@dataclass
class HtmlBuildResult:
    html: str
    warnings: list[str] = field(default_factory=list)


class RendererHost:
    """Convert renderer output into HTML using local templates."""

    def __init__(self, template_dir: Path, asset_manager: AssetManager | None = None):
        self.template_dir = template_dir
        self.asset_manager = asset_manager or AssetManager(get_vendor_assets_dir())

    def build_html(self, output: RendererOutput) -> HtmlBuildResult:
        warnings: list[str] = []
        if output.output_type == "plotly_json":
            template = self._read_template("plotly_host.html")
            asset = self.asset_manager.get_plotly_asset()
            if not asset.use_local:
                warnings.append("Local Plotly asset not found. Preview is using CDN fallback.")
            html = template.replace("{{PLOTLY_SCRIPT_REF}}", self.asset_manager.asset_script_reference(asset))
            html = html.replace("{{PLOTLY_CONFIG_JSON}}", output.content)
            html = html.replace("{{MERMAID_SCRIPT_REF}}", "")
            html = html.replace("{{CHARTJS_SCRIPT_REF}}", "")
            html = html.replace("{{MERMAID_CODE}}", "")
            html = html.replace("{{CHARTJS_CONFIG_JSON}}", "")
            return HtmlBuildResult(html=html, warnings=warnings)
        if output.output_type == "mermaid":
            template = self._read_template("mermaid_host.html")
            asset = self.asset_manager.get_mermaid_asset()
            if not asset.use_local:
                warnings.append("Local Mermaid asset not found. Preview is using CDN fallback.")
            html = template.replace("{{MERMAID_SCRIPT_REF}}", self.asset_manager.asset_script_reference(asset))
            html = html.replace("{{MERMAID_CODE}}", output.content)
            html = html.replace("{{PLOTLY_SCRIPT_REF}}", "")
            html = html.replace("{{CHARTJS_SCRIPT_REF}}", "")
            html = html.replace("{{PLOTLY_CONFIG_JSON}}", "")
            html = html.replace("{{CHARTJS_CONFIG_JSON}}", "")
            return HtmlBuildResult(html=html, warnings=warnings)
        if output.output_type == "chartjs_json":
            template = self._read_template("chartjs_host.html")
            asset = self.asset_manager.get_chartjs_asset()
            if not asset.use_local:
                warnings.append("Local Chart.js asset not found. Preview is using CDN fallback.")
            html = template.replace("{{CHARTJS_SCRIPT_REF}}", self.asset_manager.asset_script_reference(asset))
            html = html.replace("{{CHARTJS_CONFIG_JSON}}", output.content)
            html = html.replace("{{PLOTLY_SCRIPT_REF}}", "")
            html = html.replace("{{MERMAID_SCRIPT_REF}}", "")
            html = html.replace("{{PLOTLY_CONFIG_JSON}}", "")
            html = html.replace("{{MERMAID_CODE}}", "")
            return HtmlBuildResult(html=html, warnings=warnings)
        raise ValueError(f"Unsupported renderer output type: {output.output_type}")

    def _read_template(self, filename: str) -> str:
        template_path = self.template_dir / filename
        if not template_path.exists():
            raise FileNotFoundError(f"Template not found: {template_path}")
        return template_path.read_text(encoding="utf-8")
