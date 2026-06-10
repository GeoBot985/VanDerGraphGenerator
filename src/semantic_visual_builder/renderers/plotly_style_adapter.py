"""Apply neutral style intents to Plotly configs."""

from __future__ import annotations

from semantic_visual_builder.planning.visual_plan_schema import VisualPlan


class PlotlyStyleAdapter:
    def apply_style_to_config(self, plotly_config: dict, visual_plan: VisualPlan) -> dict:
        layout = dict(plotly_config.get("layout", {}))
        style = visual_plan.style
        if style.title:
            layout["title"] = style.title if not style.subtitle else f"{style.title}<br><sup>{style.subtitle}</sup>"
        elif style.subtitle:
            layout["title"] = style.subtitle
        font = layout.setdefault("font", {})
        if style.font_family:
            font["family"] = style.font_family
        if style.background:
            layout["paper_bgcolor"] = style.background
            layout["plot_bgcolor"] = style.plot_background or style.background
        if style.plot_background:
            layout["plot_bgcolor"] = style.plot_background
        if style.grid:
            show_grid = style.grid != "none"
            for axis_name in ("xaxis", "yaxis"):
                axis = layout.setdefault(axis_name, {})
                axis["showgrid"] = show_grid
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
        palette = style.palette or {}
        sequence = [
            colour
            for colour in (
                palette.get("primary"),
                palette.get("secondary"),
                palette.get("accent"),
            )
            if colour
        ]
        if sequence:
            layout["colorway"] = sequence
        plotly_config["layout"] = layout
        return plotly_config
