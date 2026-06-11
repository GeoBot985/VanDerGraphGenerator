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
    return "\n".join(lines)
