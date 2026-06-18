"""Tests for deterministic aggregation-request inference.

Covers the common "sum/avg/count of <numeric> per/by <categorical>" pattern
that previously fell through to an invalid "unknown" plan.
"""

from __future__ import annotations

from pathlib import Path

from semantic_visual_builder.data.csv_loader import CsvLoader
from semantic_visual_builder.data.data_profiler import DataProfiler
from semantic_visual_builder.planning.deterministic_fallback_mapper import (
    DeterministicFallbackMapper,
)


def _profile() -> "object":
    root = Path(__file__).resolve().parents[2]
    return DataProfiler().profile(
        CsvLoader().load(root / "assets" / "samples" / "sample_transactions.csv").dataframe
    )


def test_sum_of_amount_per_region_produces_valid_bar_plan() -> None:
    plan = DeterministicFallbackMapper().map_request_to_plan(
        "i want the sum of transaction amounts per region", _profile()
    )
    assert plan.intent == "compare_categories"
    assert plan.chart_type == "bar"
    assert plan.render_target.renderer == "plotly"
    roles = {r.role: r for r in plan.data_roles}
    assert roles["category"].field == "Region"
    assert roles["measure"].field == "Amount"
    assert roles["measure"].aggregation == "sum"


def test_average_amount_by_status_maps_aggregation() -> None:
    plan = DeterministicFallbackMapper().map_request_to_plan(
        "average amount by status", _profile()
    )
    roles = {r.role: r for r in plan.data_roles}
    assert plan.chart_type == "bar"
    assert roles["category"].field == "Status"
    assert roles["measure"].field == "Amount"
    assert roles["measure"].aggregation == "avg"


def test_count_of_transactions_per_region_uses_count_aggregation() -> None:
    plan = DeterministicFallbackMapper().map_request_to_plan(
        "count of transactions per region", _profile()
    )
    roles = {r.role: r for r in plan.data_roles}
    assert roles["category"].field == "Region"
    assert roles["measure"].aggregation == "count"


def test_total_amount_per_region_defaults_to_sum() -> None:
    plan = DeterministicFallbackMapper().map_request_to_plan(
        "total amount per region", _profile()
    )
    roles = {r.role: r for r in plan.data_roles}
    assert roles["measure"].field == "Amount"
    assert roles["measure"].aggregation == "sum"


def test_no_grouping_and_no_aggregation_stays_unknown() -> None:
    plan = DeterministicFallbackMapper().map_request_to_plan(
        "something completely unrelated", _profile()
    )
    assert plan.intent == "unknown"
    assert plan.chart_type is None


def test_explicit_chart_keyword_still_wins_over_inference() -> None:
    plan = DeterministicFallbackMapper().map_request_to_plan(
        "show a scatter of amount per region", _profile()
    )
    assert plan.chart_type == "scatter"
