"""Plotly renderer tests."""

from pathlib import Path

import pytest

from semantic_visual_builder.data.csv_loader import CsvLoader
from semantic_visual_builder.data.dataset_context import DatasetContext
from semantic_visual_builder.data.data_profiler import DataProfiler
from semantic_visual_builder.planning.field_mapper import FieldMapper
from semantic_visual_builder.planning.intent_mapper import IntentMapper
from semantic_visual_builder.renderers.plotly_renderer import PlotlyRenderer


def _sample_context() -> DatasetContext:
    root = Path(__file__).resolve().parents[2]
    loaded = CsvLoader().load(root / "assets" / "samples" / "sample_transactions.csv")
    return DatasetContext(loaded_dataset=loaded, profile=DataProfiler().profile(loaded.dataframe))


def _trend_plan():
    context = _sample_context()
    plan = IntentMapper().map_request_to_plan("Show transactions per week", context.profile)
    return FieldMapper().propose_roles("Show transactions per week", context.profile, plan), context


def test_can_render_returns_true_for_chart_plans() -> None:
    plan, _ = _trend_plan()
    assert PlotlyRenderer().can_render(plan) is True


def test_transactions_per_week_returns_plotly_json() -> None:
    plan, context = _trend_plan()
    output = PlotlyRenderer().render(plan, context)
    assert output.output_type == "plotly_json"
    assert '"data"' in output.content
    assert '"layout"' in output.content


def test_bar_chart_output_has_type_bar() -> None:
    context = _sample_context()
    plan = FieldMapper().propose_roles("Show transactions by region", context.profile, IntentMapper().map_request_to_plan("Show transactions by region", context.profile))
    output = PlotlyRenderer().render(plan, context)
    assert '"type": "bar"' in output.content


def test_horizontal_bar_output_has_orientation_h() -> None:
    context = _sample_context()
    plan = IntentMapper().map_request_to_plan("Show transactions by region", context.profile)
    plan.chart_type = "horizontal_bar"
    plan = FieldMapper().propose_roles("Show transactions by region", context.profile, plan)
    output = PlotlyRenderer().render(plan, context)
    assert '"orientation": "h"' in output.content


def test_line_chart_output_uses_scatter_trace_with_lines_markers() -> None:
    plan, context = _trend_plan()
    output = PlotlyRenderer().render(plan, context)
    assert '"type": "scatter"' in output.content
    assert '"mode": "lines+markers"' in output.content


def test_missing_dataset_raises_clear_error() -> None:
    plan, _ = _trend_plan()
    with pytest.raises(ValueError):
        PlotlyRenderer().render(plan, DatasetContext())
