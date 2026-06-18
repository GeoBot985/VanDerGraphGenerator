"""User settings schema."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class AppSettings:
    default_ollama_model: str | None = "granite4:3b"
    ollama_base_url: str = "http://localhost:11434"
    generation_timeout_seconds: float = 300.0
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
            "ollama_base_url": self.ollama_base_url,
            "generation_timeout_seconds": self.generation_timeout_seconds,
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
            ollama_base_url=str(data.get("ollama_base_url", "http://localhost:11434")) or "http://localhost:11434",
            generation_timeout_seconds=_coerce_timeout(data.get("generation_timeout_seconds", 300.0)),
            llm_mapping_enabled=bool(data.get("llm_mapping_enabled", True)),
            default_renderer=str(data.get("default_renderer", "plotly")),
            default_export_dir=data.get("default_export_dir"),
            prefer_local_renderer_assets=bool(data.get("prefer_local_renderer_assets", True)),
            open_preview_after_generation=bool(data.get("open_preview_after_generation", True)),
            default_style_profile_id=data.get("default_style_profile_id"),
            debug_mode=bool(data.get("debug_mode", False)),
        )


def _coerce_timeout(value: object) -> float:
    try:
        timeout = float(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return 300.0
    return timeout if timeout > 0 else 300.0
