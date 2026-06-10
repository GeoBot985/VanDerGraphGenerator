"""Visual plan schema stubs."""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class DataMapping:
    """Placeholder data mapping schema."""

    roles: dict[str, str] = field(default_factory=dict)


@dataclass
class StyleIntent:
    """Placeholder styling schema."""

    settings: dict[str, Any] = field(default_factory=dict)


@dataclass
class RenderTarget:
    """Placeholder render target schema."""

    renderer: str
    output: str | None = None


@dataclass
class VisualPlan:
    """Neutral visual plan placeholder."""

    visual_kind: str
    intent: str
    renderer: str | None = None
    chart_type: str | None = None
    diagram_type: str | None = None
    data_mapping: dict[str, Any] = field(default_factory=dict)
    style: dict[str, Any] = field(default_factory=dict)
