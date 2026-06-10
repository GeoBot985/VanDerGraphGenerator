"""Build standalone HTML previews from renderer output."""

from __future__ import annotations

from pathlib import Path

from semantic_visual_builder.renderers.renderer_result import RendererOutput


class RendererHost:
    """Convert renderer output into HTML using local templates."""

    def __init__(self, template_dir: Path):
        self.template_dir = template_dir

    def build_html(self, output: RendererOutput) -> str:
        if output.output_type == "plotly_json":
            template = self._read_template("plotly_host.html")
            return template.replace("{{PLOTLY_CONFIG_JSON}}", output.content)
        if output.output_type == "mermaid":
            template = self._read_template("mermaid_host.html")
            return template.replace("{{MERMAID_CODE}}", output.content)
        if output.output_type == "chartjs_json":
            template = self._read_template("chartjs_host.html")
            return template.replace("{{CHARTJS_CONFIG_JSON}}", output.content)
        raise ValueError(f"Unsupported renderer output type: {output.output_type}")

    def _read_template(self, filename: str) -> str:
        template_path = self.template_dir / filename
        if not template_path.exists():
            raise FileNotFoundError(f"Template not found: {template_path}")
        return template_path.read_text(encoding="utf-8")
