"""Renderer output models."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class RendererOutput:
    renderer_name: str
    output_type: str
    content: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class RenderedPreview:
    renderer_output: RendererOutput
    html_path: Path | None = None
    warnings: list[str] = field(default_factory=list)
