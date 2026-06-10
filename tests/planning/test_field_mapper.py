"""Field mapper tests."""

from pathlib import Path

from semantic_visual_builder.data.csv_loader import CsvLoader
from semantic_visual_builder.data.data_profiler import DataProfiler
from semantic_visual_builder.planning.field_mapper import FieldMapper
from semantic_visual_builder.planning.intent_mapper import IntentMapper


def _sample_profile():
    root = Path(__file__).resolve().parents[2]
    return DataProfiler().profile(CsvLoader().load(root / "assets" / "samples" / "sample_transactions.csv").dataframe)


def test_weekly_trend_uses_transaction_date_and_count() -> None:
    profile = _sample_profile()
    plan = IntentMapper().map_request_to_plan("Show transactions per week", profile)
    mapped = FieldMapper().propose_roles("Show transactions per week", profile, plan)
    roles = {role.role: role for role in mapped.data_roles}
    assert roles["x"].field == "TransactionDate"
    assert roles["x"].transform == "week"
    assert roles["y"].field == "row_count"


def test_amount_by_region_uses_region_and_amount() -> None:
    profile = _sample_profile()
    plan = IntentMapper().map_request_to_plan("Amount by region", profile)
    mapped = FieldMapper().propose_roles("Amount by region", profile, plan)
    roles = {role.role: role for role in mapped.data_roles}
    assert roles["category"].field == "Region"
    assert roles["measure"].field == "Amount"


def test_transactions_by_status_uses_status_and_count() -> None:
    profile = _sample_profile()
    plan = IntentMapper().map_request_to_plan("Transactions by status", profile)
    mapped = FieldMapper().propose_roles("Transactions by status", profile, plan)
    roles = {role.role: role for role in mapped.data_roles}
    assert roles["category"].field == "Status"
    assert roles["measure"].field == "row_count"
