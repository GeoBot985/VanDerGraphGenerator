"""Summarize style profiles."""

from __future__ import annotations

from .style_schema import StyleProfile


def summarize_style(style: StyleProfile) -> str:
    lines = [f"Style: {style.style_name}"]
    if style.metadata.description:
        lines.append(f"Description: {style.metadata.description}")
    lines.append(f"Supported: {', '.join(style.supported_visual_kinds)}")
    lines.append(f"Renderers: {', '.join(style.supported_renderers)}")
    lines.append("Chart:")
    if style.chart.background:
        lines.append(f"- Background: {style.chart.background}")
    if style.chart.plot_background:
        lines.append(f"- Plot background: {style.chart.plot_background}")
    if style.chart.grid:
        lines.append(f"- Grid: {style.chart.grid}")
    if style.chart.legend_position:
        lines.append(f"- Legend: {style.chart.legend_position}")
    lines.append("Typography:")
    if style.typography.font_family:
        lines.append(f"- Font: {style.typography.font_family}")
    if style.typography.title_size:
        lines.append(f"- Title size: {style.typography.title_size}")
    lines.append("Palette:")
    if style.palette.primary:
        lines.append(f"- Primary: {style.palette.primary}")
    if style.palette.secondary:
        lines.append(f"- Secondary: {style.palette.secondary}")
    if style.palette.accent:
        lines.append(f"- Accent: {style.palette.accent}")
    if style.palette.sequence:
        lines.append(f"- Sequence: {', '.join(style.palette.sequence[:5])}")

    three_d = getattr(style, "three_d", None)
    if three_d is not None:
        chart_style = three_d.chart_style or "flat"
        bits = [f"- 3D treatment: {chart_style}"]
        if three_d.depth is not None:
            bits.append(f"depth={three_d.depth}")
        if three_d.bevel is not None:
            bits.append(f"bevel={three_d.bevel}")
        if three_d.perspective is not None:
            bits.append(f"perspective={three_d.perspective}")
        if three_d.lighting is not None:
            bits.append(f"lighting={three_d.lighting}")
        if three_d.shadow is not None:
            bits.append(f"shadow={three_d.shadow}")
        if three_d.tilt is not None:
            bits.append(f"tilt={three_d.tilt}")
        if chart_style != "flat" or any(
            getattr(three_d, field) is not None
            for field in ("depth", "bevel", "perspective", "lighting", "shadow", "tilt")
        ):
            lines.append(" ".join(bits))

    return "\n".join(lines)
