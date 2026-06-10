"""Intent mapper tests."""

from pathlib import Path

from semantic_visual_builder.data.csv_loader import CsvLoader
from semantic_visual_builder.data.data_profiler import DataProfiler
from semantic_visual_builder.knowledge.graph_matrix import GraphMatrixLoader
from semantic_visual_builder.planning.intent_mapper import IntentMapper


def _sample_profile():
    root = Path(__file__).resolve().parents[2]
    return DataProfiler().profile(CsvLoader().load(root / "assets" / "samples" / "sample_transactions.csv").dataframe)


def test_transactions_per_week_maps_to_line_trend() -> None:
    plan = IntentMapper().map_request_to_plan("Show transactions per week", _sample_profile())
    assert plan.intent == "show_trend"
    assert plan.chart_type == "line"
    assert plan.visual_kind == "chart"


def test_amount_by_region_maps_to_bar() -> None:
    plan = IntentMapper().map_request_to_plan("Amount by region", _sample_profile())
    assert plan.intent == "compare_categories"
    assert plan.chart_type == "bar"


def test_relationship_maps_to_scatter() -> None:
    plan = IntentMapper().map_request_to_plan("Relationship between Amount and Count", _sample_profile())
    assert plan.intent == "show_relationship"
    assert plan.chart_type == "scatter"


def test_process_request_maps_to_flowchart() -> None:
    plan = IntentMapper().map_request_to_plan("Create a flowchart", _sample_profile())
    assert plan.intent == "show_process"
    assert plan.diagram_type == "flowchart"
