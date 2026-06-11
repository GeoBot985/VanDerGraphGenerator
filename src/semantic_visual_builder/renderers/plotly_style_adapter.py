"""Apply style intents to Plotly configs, with dark/light extracted style support."""

from __future__ import annotations

from semantic_visual_builder.planning.visual_plan_schema import VisualPlan


def _is_dark_colour(hex_value: str | None) -> bool:
    if not hex_value:
        return False
    text = hex_value.lstrip("#")
    if len(text) == 3:
        text = "".join(c * 2 for c in text)
    if len(text) != 6:
        return False
    r, g, b = int(text[0:2], 16), int(text[2:4], 16), int(text[4:6], 16)
    return (r * 299 + g * 587 + b * 114) / 1000 < 80


def _muted_grid_colour(background: str | None) -> str:
    """Return a subtle grid line colour appropriate for the background."""
    if _is_dark_colour(background):
        return "rgba(255,255,255,0.12)"
    return "rgba(0,0,0,0.10)"


class PlotlyStyleAdapter:
    def apply_style_to_config(self, plotly_config: dict, visual_plan: VisualPlan) -> dict:
        layout = dict(plotly_config.get("layout", {}))
        style = visual_plan.style

        title_text = None
        if style.title:
            title_text = (
                style.title
                if not style.subtitle
                else f"{style.title}<br><sup>{style.subtitle}</sup>"
            )
        elif style.subtitle:
            title_text = style.subtitle
        if title_text is not None:
            if style.title_size:
                layout["title"] = {"text": title_text, "font": {"size": style.title_size}}
            else:
                layout["title"] = title_text

        background = style.background
        plot_background = style.plot_background or background
        is_dark = _is_dark_colour(background)

        if background:
            layout["paper_bgcolor"] = background
        if plot_background:
            layout["plot_bgcolor"] = plot_background

        font = layout.setdefault("font", {})
        if style.font_family:
            font["family"] = style.font_family
        if is_dark:
            font.setdefault("color", "#ffffff")
        else:
            font.setdefault("color", "#000000")

        if style.grid:
            show_grid = style.grid != "none"
            grid_colour = _muted_grid_colour(background)
            for axis_name in ("xaxis", "yaxis"):
                axis = layout.setdefault(axis_name, {})
                axis["showgrid"] = show_grid
                if show_grid:
                    axis["gridcolor"] = grid_colour
                if is_dark:
                    axis["linecolor"] = "rgba(255,255,255,0.2)"
                    axis.setdefault("color", "#ffffff")

        if style.legend_position:
            legend = layout.setdefault("legend", {})
            if style.legend_position == "none":
                legend["orientation"] = "h"
                legend["y"] = -0.25
                legend["x"] = 0.0
                legend["tracegroupgap"] = 0
            elif style.legend_position == "bottom":
                legend["orientation"] = "h"
                legend["y"] = -0.25
                legend["x"] = 0.0
            else:
                legend["x"] = 1.0
                legend["y"] = 1.0

        palette = style.palette if isinstance(style.palette, dict) else {}
        sequence_from_palette = palette.get("sequence") if isinstance(palette, dict) else None
        if isinstance(sequence_from_palette, list) and sequence_from_palette:
            layout["colorway"] = [str(c) for c in sequence_from_palette if c]
        else:
            sequence = [
                colour
                for colour in (
                    palette.get("primary") if isinstance(palette, dict) else None,
                    palette.get("secondary") if isinstance(palette, dict) else None,
                    palette.get("accent") if isinstance(palette, dict) else None,
                )
                if colour
            ]
            if sequence:
                layout["colorway"] = sequence

        plotly_config["layout"] = layout
        return plotly_config
