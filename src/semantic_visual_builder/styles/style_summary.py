"""Summarize style profiles."""

from __future__ import annotations

from .style_schema import StyleProfile


def summarize_style(style: StyleProfile) -> str:
    lines = [f"Style: {style.style_name}"]
    if style.metadata.description:
        lines.append(f"Description: {style.metadata.description}")
    lines.append(f"Supported: {', '.join(style.supported_visual_kinds)}")
    lines.append(f"Renderers: {', '.join(style.supported_renderers)}")
    lines.append("Palette:")
    if style.palette.primary:
        lines.append(f"- Primary: {style.palette.primary}")
    if style.palette.secondary:
        lines.append(f"- Secondary: {style.palette.secondary}")
    if style.palette.accent:
        lines.append(f"- Accent: {style.palette.accent}")
    return "\n".join(lines)
