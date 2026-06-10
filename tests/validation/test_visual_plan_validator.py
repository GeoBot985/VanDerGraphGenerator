"""Visual plan validator tests."""

from pathlib import Path

from semantic_visual_builder.data.csv_loader import CsvLoader
from semantic_visual_builder.data.data_profiler import DataProfiler
from semantic_visual_builder.planning.field_mapper import FieldMapper
from semantic_visual_builder.planning.intent_mapper import IntentMapper
from semantic_visual_builder.planning.visual_plan_schema import DataRole, StyleIntent, VisualPlan
from semantic_visual_builder.validation.visual_plan_validator import VisualPlanValidator


def _sample_profile():
    root = Path(__file__).resolve().parents[2]
    return DataProfiler().profile(CsvLoader().load(root / "assets" / "samples" / "sample_transactions.csv").dataframe)


def test_valid_trend_plan_passes() -> None:
    profile = _sample_profile()
    plan = IntentMapper().map_request_to_plan("Show transactions per week", profile)
    plan = FieldMapper().propose_roles("Show transactions per week", profile, plan)
    result = VisualPlanValidator().validate(plan, profile)
    assert result.is_valid is True


def test_missing_x_role_fails() -> None:
    profile = _sample_profile()
    plan = VisualPlan(visual_kind="chart", intent="compare_categories", chart_type="bar", data_roles=[DataRole(role="y", field="Amount")])
    result = VisualPlanValidator().validate(plan, profile)
    assert result.is_valid is False


def test_line_chart_with_non_date_x_warns() -> None:
    profile = _sample_profile()
    plan = VisualPlan(
        visual_kind="chart",
        intent="show_trend",
        chart_type="line",
        data_roles=[DataRole(role="x", field="Region"), DataRole(role="y", field="row_count", aggregation="count")],
    )
    result = VisualPlanValidator().validate(plan, profile)
    assert result.is_valid is True
    assert any(message.severity.value == "warning" for message in result.messages)


def test_scatter_requires_numeric_axes() -> None:
    profile = _sample_profile()
    plan = VisualPlan(
        visual_kind="chart",
        intent="show_relationship",
        chart_type="scatter",
        data_roles=[DataRole(role="x", field="Region"), DataRole(role="y", field="Status")],
    )
    result = VisualPlanValidator().validate(plan, profile)
    assert result.is_valid is False


def test_missing_chart_type_fails() -> None:
    profile = _sample_profile()
    plan = VisualPlan(visual_kind="chart", intent="compare_categories", data_roles=[DataRole(role="category", field="Region"), DataRole(role="measure", field="Amount")])
    result = VisualPlanValidator().validate(plan, profile)
    assert result.is_valid is False
