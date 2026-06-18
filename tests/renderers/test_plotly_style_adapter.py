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


def test_plotly_style_adapter_handles_string_axis_title() -> None:
    """Chart builders set axis titles as plain strings; the adapter must not
    crash when a style applies a label font size on top of that."""
    plan = VisualPlan(visual_kind="chart", intent="compare")
    plan.style.label_size = 14
    plan.style.background = "#ffffff"
    config = {
        "layout": {
            "xaxis": {"title": "Region"},
            "yaxis": {"title": "Amount"},
        }
    }
    result = PlotlyStyleAdapter().apply_style_to_config(config, plan)
    assert result["layout"]["xaxis"]["title"] == {"text": "Region", "font": {"size": 14}}
    assert result["layout"]["yaxis"]["title"] == {"text": "Amount", "font": {"size": 14}}


def test_plotly_style_adapter_handles_dict_axis_title() -> None:
    plan = VisualPlan(visual_kind="chart", intent="compare")
    plan.style.label_size = 12
    plan.style.background = "#ffffff"
    config = {"layout": {"xaxis": {"title": {"text": "Region", "font": {"color": "#000"}}}}}
    result = PlotlyStyleAdapter().apply_style_to_config(config, plan)
    # Existing dict title is preserved and font size added.
    assert result["layout"]["xaxis"]["title"]["text"] == "Region"
    assert result["layout"]["xaxis"]["title"]["font"]["size"] == 12
    assert result["layout"]["xaxis"]["title"]["font"]["color"] == "#000"


def test_large_title_size_grows_top_margin_so_it_is_not_clipped() -> None:
    plan = VisualPlan(visual_kind="chart", intent="compare")
    plan.style.title = "Regional Transaction Amounts"
    plan.style.subtitle = "by region"
    plan.style.title_size = 48
    plan.style.background = "#ffffff"
    config = {"layout": {"margin": {"l": 60, "r": 30, "t": 60, "b": 60}}}
    result = PlotlyStyleAdapter().apply_style_to_config(config, plan)
    margin_t = result["layout"]["margin"]["t"]
    # Base room for the title plus the subtitle line.
    assert margin_t >= 48 + 40
    assert margin_t > 60, "top margin must grow for large title fonts"


def test_default_title_size_keeps_reasonable_top_margin() -> None:
    plan = VisualPlan(visual_kind="chart", intent="compare")
    plan.style.title = "Title"
    plan.style.title_size = 18
    plan.style.background = "#ffffff"
    config = {"layout": {"margin": {"l": 60, "r": 30, "t": 60, "b": 60}}}
    result = PlotlyStyleAdapter().apply_style_to_config(config, plan)
    # A small title should not need more than the builder default.
    assert result["layout"]["margin"]["t"] == 60
    assert result["layout"]["xaxis"]["automargin"] is True

