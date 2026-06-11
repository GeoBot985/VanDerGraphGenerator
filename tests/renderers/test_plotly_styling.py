"""Plotly styling tests."""

from pathlib import Path

from semantic_visual_builder.data.csv_loader import CsvLoader
from semantic_visual_builder.data.data_profiler import DataProfiler
from semantic_visual_builder.data.dataset_context import DatasetContext
from semantic_visual_builder.planning.field_mapper import FieldMapper
from semantic_visual_builder.planning.intent_mapper import IntentMapper
from semantic_visual_builder.planning.visual_plan import get_role
from semantic_visual_builder.renderers.plotly_renderer import PlotlyRenderer


def _sample_context() -> DatasetContext:
    root = Path(__file__).resolve().parents[2]
    loaded = CsvLoader().load(root / "assets" / "samples" / "sample_transactions.csv")
    return DatasetContext(loaded_dataset=loaded, profile=DataProfiler().profile(loaded.dataframe))


def test_style_title_appears_in_layout() -> None:
    context = _sample_context()
    plan = FieldMapper().propose_roles("Show amount by region", context.profile, IntentMapper().map_request_to_plan("Show amount by region", context.profile))
    plan.style.title = "Custom Title"
    output = PlotlyRenderer().render(plan, context)
    assert '"title": "Custom Title"' in output.content


def test_horizontal_orientation_creates_horizontal_bar() -> None:
    context = _sample_context()
    plan = FieldMapper().propose_roles("Show amount by region", context.profile, IntentMapper().map_request_to_plan("Show amount by region", context.profile))
    plan.chart_type = "horizontal_bar"
    plan.style.orientation = "horizontal"
    output = PlotlyRenderer().render(plan, context)
    assert '"orientation": "h"' in output.content


def test_blue_colour_scheme_maps_to_marker_colour() -> None:
    context = _sample_context()
    plan = FieldMapper().propose_roles("Show amount by region", context.profile, IntentMapper().map_request_to_plan("Show amount by region", context.profile))
    plan.style.colour_scheme = "blue"
    output = PlotlyRenderer().render(plan, context)
    assert "#4C78A8" in output.content


def test_primary_palette_colour_overrides_default_bar_colour() -> None:
    context = _sample_context()
    plan = FieldMapper().propose_roles("Show amount by region", context.profile, IntentMapper().map_request_to_plan("Show amount by region", context.profile))
    plan.style.palette = {"primary": "#d3d3d3"}
    output = PlotlyRenderer().render(plan, context)
    assert "#d3d3d3" in output.content


def test_highlight_category_produces_marker_colour_list() -> None:
    context = _sample_context()
    plan = FieldMapper().propose_roles("Show amount by region", context.profile, IntentMapper().map_request_to_plan("Show amount by region", context.profile))
    plan.style.highlights = {"value": "Gauteng"}
    output = PlotlyRenderer().render(plan, context)
    assert "marker" in output.content


def test_unsupported_highlight_creates_warning_metadata() -> None:
    context = _sample_context()
    plan = FieldMapper().propose_roles("Show amount by region", context.profile, IntentMapper().map_request_to_plan("Show amount by region", context.profile))
    plan.style.highlights = {"field": "Status", "value": "Failed"}
    output = PlotlyRenderer().render(plan, context)
    assert "warnings" in output.metadata
    assert output.metadata["warnings"]
