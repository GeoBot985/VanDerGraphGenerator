"""Advanced deterministic field mapping tests."""

from semantic_visual_builder.data.data_profiler import ColumnProfile, DatasetProfile
from semantic_visual_builder.planning.field_mapper import FieldMapper
from semantic_visual_builder.planning.intent_mapper import IntentMapper
from semantic_visual_builder.planning.visual_plan import get_role


def _profile() -> DatasetProfile:
    return DatasetProfile(
        row_count=24,
        column_count=5,
        columns=[
            ColumnProfile("Region", "object", "categorical", 0, 0.0, 4, ["Gauteng"]),
            ColumnProfile("Status", "object", "categorical", 0, 0.0, 3, ["Failed"]),
            ColumnProfile("TransactionDate", "datetime64[ns]", "datetime", 0, 0.0, 12, ["2024-01-01"]),
            ColumnProfile("Amount", "float64", "numeric", 0, 0.0, 24, ["10.0"]),
            ColumnProfile("Quantity", "float64", "numeric", 0, 0.0, 18, ["2.0"]),
        ],
    )


def _map(message: str):
    profile = _profile()
    plan = IntentMapper().map_request_to_plan(message, profile)
    return FieldMapper().propose_roles(message, profile, plan)


def test_amount_by_region_maps_region_amount_and_sum() -> None:
    plan = _map("amount by region")
    assert get_role(plan, "category").field == "Region"
    assert get_role(plan, "measure").field == "Amount"
    assert get_role(plan, "measure").aggregation == "sum"


def test_average_amount_by_status_maps_status_amount_and_avg() -> None:
    plan = _map("average amount by status")
    assert get_role(plan, "category").field == "Status"
    assert get_role(plan, "measure").field == "Amount"
    assert get_role(plan, "measure").aggregation == "avg"


def test_failed_transactions_per_week_maps_date_count_and_filter() -> None:
    plan = _map("failed transactions per week")
    assert get_role(plan, "x").field == "TransactionDate"
    assert get_role(plan, "x").transform == "week"
    assert get_role(plan, "y").field == "row_count"
    assert any(item["field"] == "Status" and item["value"] == "Failed" for item in plan.filters)


def test_approved_amount_by_region_maps_filter_and_measure() -> None:
    plan = _map("approved amount by region")
    assert get_role(plan, "category").field == "Region"
    assert get_role(plan, "measure").field == "Amount"
    assert any(item["field"] == "Status" and item["value"] == "Approved" for item in plan.filters)
