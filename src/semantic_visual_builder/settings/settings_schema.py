"""User settings schema."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class AppSettings:
    default_ollama_model: str | None = None
    llm_mapping_enabled: bool = True
    default_renderer: str = "plotly"
    default_export_dir: str | None = None
    prefer_local_renderer_assets: bool = True
    open_preview_after_generation: bool = True
    default_style_profile_id: str | None = None
    debug_mode: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "default_ollama_model": self.default_ollama_model,
            "llm_mapping_enabled": self.llm_mapping_enabled,
            "default_renderer": self.default_renderer,
            "default_export_dir": self.default_export_dir,
            "prefer_local_renderer_assets": self.prefer_local_renderer_assets,
            "open_preview_after_generation": self.open_preview_after_generation,
            "default_style_profile_id": self.default_style_profile_id,
            "debug_mode": self.debug_mode,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "AppSettings":
        return cls(
            default_ollama_model=data.get("default_ollama_model"),
            llm_mapping_enabled=bool(data.get("llm_mapping_enabled", True)),
            default_renderer=str(data.get("default_renderer", "plotly")),
            default_export_dir=data.get("default_export_dir"),
            prefer_local_renderer_assets=bool(data.get("prefer_local_renderer_assets", True)),
            open_preview_after_generation=bool(data.get("open_preview_after_generation", True)),
            default_style_profile_id=data.get("default_style_profile_id"),
            debug_mode=bool(data.get("debug_mode", False)),
        )
