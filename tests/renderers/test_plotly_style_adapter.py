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


def test_plotly_style_adapter_applies_font_weight() -> None:
    plan = VisualPlan(visual_kind="chart", intent="compare")
    plan.style.font_weight = "bold"

    config = PlotlyStyleAdapter().apply_style_to_config({"layout": {}}, plan)

    assert config["layout"]["font"]["weight"] == 700


def test_plotly_style_adapter_applies_bar_gap() -> None:
    plan = VisualPlan(visual_kind="chart", intent="compare")
    plan.style.bar_gap = 0.4

    config = PlotlyStyleAdapter().apply_style_to_config({"layout": {}}, plan)

    assert config["layout"]["bargap"] == 0.4


def test_plotly_style_adapter_applies_title_alignment() -> None:
    plan = VisualPlan(visual_kind="chart", intent="compare")
    plan.style.title = "My Chart"
    plan.style.title_alignment = "center"

    config = PlotlyStyleAdapter().apply_style_to_config({"layout": {}}, plan)

    assert config["layout"]["title"]["x"] == 0.5
    assert config["layout"]["title"]["xanchor"] == "center"


def test_plotly_style_adapter_applies_line_shape_to_scatter_traces() -> None:
    plan = VisualPlan(visual_kind="chart", intent="compare")
    plan.style.line_shape = "spline"
    data = [{"type": "scatter", "x": [1], "y": [1]}, {"type": "bar", "x": [1], "y": [1]}]

    config = PlotlyStyleAdapter().apply_style_to_config({"layout": {}, "data": data}, plan)

    assert config["data"][0]["line"]["shape"] == "spline"
    assert "line" not in config["data"][1]


def test_plotly_style_adapter_applies_tick_sizes() -> None:
    plan = VisualPlan(visual_kind="chart", intent="compare")
    plan.style.label_size = 14
    plan.style.tick_size = 11

    config = PlotlyStyleAdapter().apply_style_to_config({"layout": {}}, plan)

    assert config["layout"]["xaxis"]["tickfont"]["size"] == 11
    assert config["layout"]["yaxis"]["tickfont"]["size"] == 11
