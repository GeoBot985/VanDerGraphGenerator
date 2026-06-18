"""Style profile schema models."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass
class StyleMetadata:
    style_id: str
    style_name: str
    description: str | None = None
    schema_version: str = "1.0"
    created_at: str | None = None
    updated_at: str | None = None
    author: str | None = None
    tags: list[str] = field(default_factory=list)


@dataclass
class ColourPalette:
    primary: str | None = None
    secondary: str | None = None
    accent: str | None = None
    neutral: str | None = None
    warning: str | None = None
    success: str | None = None
    danger: str | None = None
    sequence: list[str] = field(default_factory=list)


@dataclass
class TypographyStyle:
    font_family: str | None = None
    font_weight: str | None = None  # "normal" | "bold"
    title_size: int | None = None
    label_size: int | None = None
    tick_size: int | None = None


@dataclass
class ChartStyle:
    background: str | None = None
    plot_background: str | None = None
    grid: str | None = None
    legend_position: str | None = None
    label_density: str | None = None
    title_alignment: str | None = None
    bar_gap: float | None = None
    line_shape: str | None = None


@dataclass
class DiagramStyle:
    direction: str | None = None
    node_fill: str | None = None
    node_stroke: str | None = None
    decision_fill: str | None = None
    edge_colour: str | None = None
    border_radius: int | None = None   # px  - 0 = sharp, 8 = rounded
    stroke_width: int | None = None    # px  - 1 = thin, 2 = medium, 3 = thick
    class_defs: dict[str, dict[str, Any]] = field(default_factory=dict)


@dataclass
class ThreeDStyle:
    """3D treatment that a style profile requests of the renderer.

    ``chart_style`` chooses the overall feel:
      - ``flat`` (default): standard 2D rendering, no perspective or extrusion.
      - ``soft_3d``: extruded bars / layered markers but still 2D layout,
        readable in print and small viewports.
      - ``true_3d``: full Plotly 3D scene with camera tilt and lighting.

    The remaining knobs only affect non-flat styles but are always validated so
    style authors can express their intent precisely.
    """

    chart_style: str | None = None       # "flat" | "soft_3d" | "true_3d"
    depth: int | None = None             # px extrusion
    bevel: int | None = None             # px bevel radius
    perspective: float | None = None     # 0.0-1.0
    lighting: str | None = None          # "flat" | "soft" | "dramatic"
    shadow: bool | None = None
    tilt: int | None = None              # deg camera tilt


@dataclass
class RendererStyleHints:
    plotly_template: str | None = None
    mermaid_theme: str | None = None
    chartjs_options: dict[str, Any] = field(default_factory=dict)


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class StyleProfile:
    metadata: StyleMetadata
    palette: ColourPalette = field(default_factory=ColourPalette)
    typography: TypographyStyle = field(default_factory=TypographyStyle)
    chart: ChartStyle = field(default_factory=ChartStyle)
    diagram: DiagramStyle = field(default_factory=DiagramStyle)
    three_d: ThreeDStyle = field(default_factory=ThreeDStyle)
    renderer_hints: RendererStyleHints = field(default_factory=RendererStyleHints)
    supported_visual_kinds: list[str] = field(default_factory=lambda: ["chart", "diagram"])
    supported_renderers: list[str] = field(default_factory=lambda: ["plotly", "mermaid", "chartjs"])

    @property
    def style_id(self) -> str:
        return self.metadata.style_id

    @property
    def style_name(self) -> str:
        return self.metadata.style_name

    def to_dict(self) -> dict[str, Any]:
        return {
            "metadata": asdict(self.metadata),
            "palette": asdict(self.palette),
            "typography": asdict(self.typography),
            "chart": asdict(self.chart),
            "diagram": asdict(self.diagram),
            "three_d": asdict(self.three_d),
            "renderer_hints": asdict(self.renderer_hints),
            "supported_visual_kinds": list(self.supported_visual_kinds),
            "supported_renderers": list(self.supported_renderers),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "StyleProfile":
        metadata_data = data.get("metadata") or {}
        metadata = StyleMetadata(
            style_id=str(metadata_data.get("style_id", "")),
            style_name=str(metadata_data.get("style_name", "")),
            description=metadata_data.get("description"),
            schema_version=str(metadata_data.get("schema_version", "1.0")),
            created_at=metadata_data.get("created_at"),
            updated_at=metadata_data.get("updated_at"),
            author=metadata_data.get("author"),
            tags=list(metadata_data.get("tags", []) or []),
        )
        return cls(
            metadata=metadata,
            palette=ColourPalette(**(data.get("palette", {}) or {})),
            typography=TypographyStyle(**(data.get("typography", {}) or {})),
            chart=ChartStyle(**(data.get("chart", {}) or {})),
            diagram=DiagramStyle(**(data.get("diagram", {}) or {})),
            three_d=ThreeDStyle(**(data.get("three_d", {}) or {})),
            renderer_hints=RendererStyleHints(**(data.get("renderer_hints", {}) or {})),
            supported_visual_kinds=list(data.get("supported_visual_kinds", ["chart", "diagram"]) or []),
            supported_renderers=list(data.get("supported_renderers", ["plotly", "mermaid", "chartjs"]) or []),
        )
