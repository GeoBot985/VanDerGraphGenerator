"""Plotly style adapter tests."""

from semantic_visual_builder.planning.visual_plan_schema import VisualPlan
from semantic_visual_builder.renderers.plotly_style_adapter import PlotlyStyleAdapter


def test_plotly_style_adapter_updates_layout_fields() -> None:
    plan = VisualPlan(visual_kind="chart", intent="compare")
    plan.style.title = "Sales"
    plan.style.subtitle = "Quarterly"
    plan.style.font_family = "Arial"
    plan.style.background = "#ffffff"
    plan.style.plot_background = "#f7f7f7"
    plan.style.grid = "light"
    plan.style.legend_position = "bottom"
    plan.style.palette = {
        "primary": "#1f4e79",
        "secondary": "#5b9bd5",
        "accent": "#70ad47",
    }

    config = PlotlyStyleAdapter().apply_style_to_config({"layout": {}}, plan)

    assert config["layout"]["title"] == "Sales<br><sup>Quarterly</sup>"
    assert config["layout"]["font"]["family"] == "Arial"
    assert config["layout"]["paper_bgcolor"] == "#ffffff"
    assert config["layout"]["plot_bgcolor"] == "#f7f7f7"
    assert config["layout"]["legend"]["orientation"] == "h"
    assert config["layout"]["colorway"] == ["#1f4e79", "#5b9bd5", "#70ad47"]


def test_plotly_style_adapter_applies_title_size_when_present() -> None:
    plan = VisualPlan(visual_kind="chart", intent="compare")
    plan.style.title = "Sales"
    plan.style.title_size = 32

    config = PlotlyStyleAdapter().apply_style_to_config({"layout": {}}, plan)

    assert config["layout"]["title"]["text"] == "Sales"
    assert config["layout"]["title"]["font"]["size"] == 32
