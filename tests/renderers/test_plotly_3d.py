"""Tests for the chart_style / 3D plumbing in the Plotly renderer."""

from __future__ import annotations

from pathlib import Path

from semantic_visual_builder.data.csv_loader import CsvLoader
from semantic_visual_builder.data.data_profiler import DataProfiler
from semantic_visual_builder.data.dataset_context import DatasetContext
from semantic_visual_builder.planning.field_mapper import FieldMapper
from semantic_visual_builder.planning.intent_mapper import IntentMapper
from semantic_visual_builder.planning.visual_plan_schema import DataRole, VisualPlan
from semantic_visual_builder.renderers.plotly_3d import (
    bar3d_trace,
    chart_style,
    depth,
    lighting,
    perspective,
    scene,
    shadow,
    tilt,
)
from semantic_visual_builder.renderers.plotly_renderer import PlotlyRenderer


def _sample_context() -> DatasetContext:
    root = Path(__file__).resolve().parents[2]
    loaded = CsvLoader().load(root / "assets" / "samples" / "sample_transactions.csv")
    return DatasetContext(
        loaded_dataset=loaded,
        profile=DataProfiler().profile(loaded.dataframe),
    )


def _bar_plan(style: str) -> VisualPlan:
    context = _sample_context()
    plan = FieldMapper().propose_roles(
        "Show amount by region",
        context.profile,
        IntentMapper().map_request_to_plan("Show amount by region", context.profile),
    )
    plan.style.chart_style = style
    return plan


def test_chart_style_defaults_to_flat() -> None:
    plan = VisualPlan(visual_kind="chart", intent="compare")
    assert chart_style(plan) == "flat"
    plan.style.chart_style = "garbage"
    assert chart_style(plan) == "flat"


def test_depth_and_perspective_have_safe_defaults() -> None:
    plan = VisualPlan(visual_kind="chart", intent="compare")
    assert depth(plan) == 0
    assert perspective(plan) == 0.1
    plan.style.chart_style = "true_3d"
    assert depth(plan) > 0
    assert perspective(plan) > 0
    plan.style.perspective = 5.0
    assert perspective(plan) == 1.0
    plan.style.tilt = 999
    assert tilt(plan) == 180


def test_bar_renders_as_bar3d_when_true_3d() -> None:
    plan = _bar_plan("true_3d")
    output = PlotlyRenderer().render(plan, _sample_context())
    assert "bar3d" in output.content
    assert "scene" in output.content
    assert "lighting" in output.content


def test_bar_uses_extrusion_marker_when_soft_3d() -> None:
    plan = _bar_plan("soft_3d")
    output = PlotlyRenderer().render(plan, _sample_context())
    assert '"type": "bar"' in output.content
    assert "fill-opacity" in output.content
    assert "bar3d" not in output.content


def test_bar_stays_flat_when_chart_style_flat() -> None:
    plan = _bar_plan("flat")
    output = PlotlyRenderer().render(plan, _sample_context())
    assert '"type": "bar"' in output.content
    assert "bar3d" not in output.content
    assert "scene" not in output.content


def test_scatter_renders_as_scatter3d_when_true_3d() -> None:
    plan = VisualPlan(
        visual_kind="chart",
        intent="show_relationship",
        chart_type="scatter",
        data_roles=[
            DataRole(role="x", field="Amount"),
            DataRole(role="y", field="Amount"),
        ],
    )
    plan.style.chart_style = "true_3d"
    output = PlotlyRenderer().render(plan, _sample_context())
    assert "scatter3d" in output.content


def test_pie_renders_exploded_when_true_3d() -> None:
    plan = _bar_plan("true_3d")
    plan.chart_type = "pie"
    output = PlotlyRenderer().render(plan, _sample_context())
    assert "rotation" in output.content
    assert "pull" in output.content


def test_line_renders_as_scatter3d_when_true_3d() -> None:
    context = _sample_context()
    plan = IntentMapper().map_request_to_plan(
        "Show transactions per week", context.profile
    )
    plan.style.chart_style = "true_3d"
    output = PlotlyRenderer().render(plan, context)
    assert "scatter3d" in output.content


def test_scene_only_present_for_true_3d() -> None:
    plan = _bar_plan("true_3d")
    sc = scene(plan)
    assert sc
    assert sc["camera"]["eye"]["z"] > 0
    plan.style.chart_style = "soft_3d"
    assert scene(plan) == {}


def test_shadow_default_tracks_chart_style() -> None:
    plan = VisualPlan(visual_kind="chart", intent="compare")
    assert shadow(plan) is False
    plan.style.chart_style = "true_3d"
    assert shadow(plan) is True


def test_bar3d_trace_returns_bar3d_for_true_3d() -> None:
    plan = VisualPlan(visual_kind="chart", intent="compare")
    plan.style.chart_style = "true_3d"
    trace = bar3d_trace(plan, ["A", "B"], [1.0, 2.0])
    assert trace["type"] == "bar3d"
    assert "lighting" in trace


def test_bar3d_trace_falls_back_to_bar_for_soft_3d() -> None:
    plan = VisualPlan(visual_kind="chart", intent="compare")
    plan.style.chart_style = "soft_3d"
    trace = bar3d_trace(plan, ["A", "B"], [1.0, 2.0])
    assert trace["type"] == "bar"


def test_lighting_default() -> None:
    plan = VisualPlan(visual_kind="chart", intent="compare")
    plan.style.chart_style = "true_3d"
    assert lighting(plan) == "soft"
    plan.style.lighting = "dramatic"
    assert lighting(plan) == "dramatic"
    plan.style.lighting = "weird"
    assert lighting(plan) == "soft"
