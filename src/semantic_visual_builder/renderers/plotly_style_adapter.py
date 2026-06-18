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
        layout["template"] = "plotly_dark" if is_dark else "plotly_white"

        font = layout.setdefault("font", {})
        if style.font_family:
            font["family"] = style.font_family
        if style.font_weight:
            font["weight"] = 700 if style.font_weight == "bold" else 400
        if is_dark:
            font.setdefault("color", "#ffffff")
        else:
            font.setdefault("color", "#000000")

        if style.label_size or style.tick_size:
            tick_size = style.tick_size or style.label_size
            for axis_name in ("xaxis", "yaxis"):
                axis = layout.setdefault(axis_name, {})
                if style.label_size:
                    axis.setdefault("title", {}).setdefault("font", {})["size"] = style.label_size
                if tick_size:
                    axis.setdefault("tickfont", {})["size"] = tick_size

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

        if style.bar_gap is not None:
            layout["bargap"] = style.bar_gap

        if style.title_alignment:
            title_entry = layout.get("title")
            x_map = {"left": 0.0, "center": 0.5, "right": 1.0}
            anchor_map = {"left": "left", "center": "center", "right": "right"}
            x_val = x_map.get(style.title_alignment)
            if x_val is not None:
                if isinstance(title_entry, str):
                    layout["title"] = {"text": title_entry, "x": x_val, "xanchor": anchor_map[style.title_alignment]}
                elif isinstance(title_entry, dict):
                    title_entry["x"] = x_val
                    title_entry["xanchor"] = anchor_map[style.title_alignment]

        if style.line_shape:
            for trace in plotly_config.get("data", []):
                if isinstance(trace, dict) and trace.get("type") in ("scatter", "scattergl"):
                    trace.setdefault("line", {})["shape"] = style.line_shape

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
