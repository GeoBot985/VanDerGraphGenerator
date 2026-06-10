"""Manage renderer asset references."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass
class RendererAsset:
    name: str
    local_path: Path | None
    cdn_url: str
    use_local: bool


class AssetManager:
    """Resolve local or CDN references for renderer assets."""

    def __init__(self, vendor_dir: Path, prefer_local: bool = True):
        self.vendor_dir = vendor_dir
        self.prefer_local = prefer_local

    def get_plotly_asset(self) -> RendererAsset:
        return self._resolve_asset("plotly", "plotly/plotly.min.js", "https://cdn.plot.ly/plotly-latest.min.js")

    def get_mermaid_asset(self) -> RendererAsset:
        return self._resolve_asset(
            "mermaid",
            "mermaid/mermaid.min.js",
            "https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.esm.min.mjs",
        )

    def get_chartjs_asset(self) -> RendererAsset:
        return self._resolve_asset("chartjs", "chartjs/chart.umd.js", "https://cdn.jsdelivr.net/npm/chart.js")

    def asset_script_reference(self, asset: RendererAsset) -> str:
        if asset.use_local and asset.local_path is not None:
            return asset.local_path.resolve().as_uri()
        return asset.cdn_url

    def _resolve_asset(self, name: str, relative_path: str, cdn_url: str) -> RendererAsset:
        local_path = self.vendor_dir / relative_path
        use_local = self.prefer_local and local_path.exists()
        return RendererAsset(name=name, local_path=local_path if local_path.exists() else None, cdn_url=cdn_url, use_local=use_local)
