"""Clarification engine tests."""

from semantic_visual_builder.data.data_profiler import ColumnProfile, DatasetProfile
from semantic_visual_builder.planning.clarification_engine import ClarificationEngine
from semantic_visual_builder.planning.visual_plan import get_role
from semantic_visual_builder.planning.visual_plan_schema import DataRole, VisualPlan


def _profile() -> DatasetProfile:
    return DatasetProfile(
        row_count=10,
        column_count=5,
        columns=[
            ColumnProfile("Region", "object", "categorical", 0, 0.0, 3, ["Gauteng"]),
            ColumnProfile("Status", "object", "categorical", 0, 0.0, 2, ["Failed"]),
            ColumnProfile("TransactionDate", "datetime64[ns]", "datetime", 0, 0.0, 7, ["2024-01-01"]),
            ColumnProfile("ApprovedAt", "datetime64[ns]", "datetime", 0, 0.0, 4, ["2024-01-02"]),
            ColumnProfile("Amount", "float64", "numeric", 0, 0.0, 10, ["1.0"]),
        ],
    )


def test_missing_category_field_creates_clarification_request() -> None:
    plan = VisualPlan(
        visual_kind="chart",
        intent="compare_categories",
        chart_type="bar",
        data_roles=[DataRole(role="measure", field="Amount", aggregation="sum")],
    )
    requests = ClarificationEngine().detect_needed_clarification(plan, _profile())
    assert requests
    assert requests[0].field_name == "category"
    assert "category axis" in requests[0].question.lower()


def test_multiple_date_fields_creates_clarification_request() -> None:
    plan = VisualPlan(visual_kind="chart", intent="show_trend", chart_type="line", data_roles=[DataRole(role="measure", field="row_count", aggregation="count")])
    requests = ClarificationEngine().detect_needed_clarification(plan, _profile())
    assert requests
    assert any(request.field_name == "x" for request in requests)


def test_apply_answer_selects_field() -> None:
    plan = VisualPlan(visual_kind="chart", intent="show_trend", chart_type="line")
    clarification = ClarificationEngine().detect_needed_clarification(plan, _profile())[0]
    updated = ClarificationEngine().apply_answer(plan, clarification, "TransactionDate")
    assert get_role(updated, "x").field == "TransactionDate"


def test_complete_valid_plan_needs_no_clarification() -> None:
    plan = VisualPlan(
        visual_kind="chart",
        intent="compare_categories",
        chart_type="bar",
        data_roles=[
            DataRole(role="category", field="Region"),
            DataRole(role="measure", field="Amount", aggregation="sum"),
        ],
    )
    assert ClarificationEngine().detect_needed_clarification(plan, _profile()) == []
