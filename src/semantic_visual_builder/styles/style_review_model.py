"""Editable style draft for reviewing extracted styles before saving."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone

from .style_schema import (
    ChartStyle,
    ColourPalette,
    DiagramStyle,
    RendererStyleHints,
    StyleMetadata,
    StyleProfile,
    TypographyStyle,
)
from .style_validator import StyleValidator


@dataclass
class EditableStyleDraft:
    style_id: str
    style_name: str
    description: str | None = None
    primary: str | None = None
    secondary: str | None = None
    accent: str | None = None
    neutral: str | None = None
    background: str | None = None
    plot_background: str | None = None
    text_colour: str | None = None
    grid: str | None = None
    label_density: str | None = None
    chart_tone: str | None = None
    tags: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


def editable_draft_from_style_profile(style: StyleProfile) -> EditableStyleDraft:
    """Convert a StyleProfile into an editable draft for UI review."""
    return EditableStyleDraft(
        style_id=style.metadata.style_id,
        style_name=style.metadata.style_name,
        description=style.metadata.description,
        primary=style.palette.primary,
        secondary=style.palette.secondary,
        accent=style.palette.accent,
        neutral=style.palette.neutral,
        background=style.chart.background,
        plot_background=style.chart.plot_background,
        text_colour=None,
        grid=style.chart.grid,
        label_density=style.chart.label_density,
        chart_tone=next(
            (tag for tag in style.metadata.tags if tag in ("corporate", "presentation", "minimal", "technical", "playful", "dark", "neutral", "report")),
            None,
        ),
        tags=list(style.metadata.tags),
        warnings=[],
    )


def style_profile_from_editable_draft(draft: EditableStyleDraft) -> StyleProfile:
    """Convert an edited draft back to a StyleProfile ready for validation and saving."""
    now = datetime.now(timezone.utc).isoformat()
    tags = list(draft.tags)
    if draft.chart_tone and draft.chart_tone not in tags:
        tags.append(draft.chart_tone)

    metadata = StyleMetadata(
        style_id=draft.style_id,
        style_name=draft.style_name,
        description=draft.description,
        schema_version="1.0",
        created_at=now,
        updated_at=now,
        author="user-review",
        tags=sorted({t.strip().lower() for t in tags if t}),
    )
    sequence = [
        c
        for c in (draft.primary, draft.secondary, draft.accent, draft.neutral)
        if c
    ]
    palette = ColourPalette(
        primary=draft.primary,
        secondary=draft.secondary,
        accent=draft.accent,
        neutral=draft.neutral,
        sequence=sequence,
    )
    chart = ChartStyle(
        background=draft.background,
        plot_background=draft.plot_background or draft.background,
        grid=draft.grid,
        label_density=draft.label_density,
        legend_position="right",
        title_alignment="left",
    )
    node_fill = draft.background or "#d9eaf7"
    node_stroke = draft.primary or "#1f4e79"
    diagram = DiagramStyle(
        direction="TD",
        node_fill=node_fill,
        node_stroke=node_stroke,
        decision_fill=draft.accent or node_fill,
        edge_colour=node_stroke,
    )
    plotly_template = "plotly_dark" if _is_dark(draft.background) else "plotly_white"
    renderer_hints = RendererStyleHints(
        plotly_template=plotly_template,
        mermaid_theme="base",
    )
    return StyleProfile(
        metadata=metadata,
        palette=palette,
        typography=TypographyStyle(font_family="Arial"),
        chart=chart,
        diagram=diagram,
        renderer_hints=renderer_hints,
        supported_visual_kinds=["chart", "diagram"],
        supported_renderers=["plotly", "mermaid"],
    )


def validate_editable_draft(draft: EditableStyleDraft) -> list[str]:
    """Return a list of validation error strings for an editable draft."""
    profile = style_profile_from_editable_draft(draft)
    result = StyleValidator().validate_style(profile)
    return [msg.message for msg in result.messages if msg.severity.value == "error"]


def _is_dark(background: str | None) -> bool:
    if not background:
        return False
    text = background.lstrip("#")
    if len(text) != 6:
        return False
    r, g, b = int(text[0:2], 16), int(text[2:4], 16), int(text[4:6], 16)
    return (r * 299 + g * 587 + b * 114) / 1000 < 80
