"""Visual plan validator tests."""

from pathlib import Path

from semantic_visual_builder.data.csv_loader import CsvLoader
from semantic_visual_builder.data.data_profiler import DataProfiler
from semantic_visual_builder.knowledge.graph_matrix import GraphMatrixLoader
from semantic_visual_builder.planning.field_mapper import FieldMapper
from semantic_visual_builder.planning.intent_mapper import IntentMapper
from semantic_visual_builder.planning.visual_plan_schema import (
    DataRole,
    DiagramEdge,
    DiagramNode,
    VisualPlan,
)
from semantic_visual_builder.utils.paths import get_graph_matrix_dir
from semantic_visual_builder.validation.visual_plan_validator import (
    VisualPlanValidator,
)


def _sample_profile():
    root = Path(__file__).resolve().parents[2]
    return DataProfiler().profile(
        CsvLoader()
        .load(root / "assets" / "samples" / "sample_transactions.csv")
        .dataframe
    )


def _matrix():
    return GraphMatrixLoader(get_graph_matrix_dir() / "graph_matrix.json").load()


def _chart_plan(
    chart_type: str,
    roles: list[DataRole],
    intent: str = "compare_categories",
) -> VisualPlan:
    plan = VisualPlan(
        visual_kind="chart",
        intent=intent,
        chart_type=chart_type,
        data_roles=roles,
    )
    plan.render_target.renderer = "plotly"
    return plan


def test_valid_trend_plan_passes() -> None:
    profile = _sample_profile()
    plan = IntentMapper().map_request_to_plan(
        "Show transactions per week", profile, _matrix()
    )
    plan = FieldMapper().propose_roles("Show transactions per week", profile, plan)
    result = VisualPlanValidator().validate(plan, profile, _matrix())
    assert result.is_valid is True


def test_missing_x_role_fails() -> None:
    profile = _sample_profile()
    plan = _chart_plan("bar", [DataRole(role="y", field="Amount")])
    result = VisualPlanValidator().validate(plan, profile, _matrix())
    assert result.is_valid is False


def test_line_chart_with_non_date_x_warns() -> None:
    profile = _sample_profile()
    plan = _chart_plan(
        "line",
        [
            DataRole(role="x", field="Region"),
            DataRole(role="y", field="row_count", aggregation="count"),
        ],
        intent="show_trend",
    )
    result = VisualPlanValidator().validate(plan, profile, _matrix())
    assert result.is_valid is True
    assert any(message.severity.value == "warning" for message in result.messages)


def test_scatter_requires_numeric_axes() -> None:
    profile = _sample_profile()
    plan = _chart_plan(
        "scatter",
        [DataRole(role="x", field="Region"), DataRole(role="y", field="Status")],
        intent="show_relationship",
    )
    result = VisualPlanValidator().validate(plan, profile, _matrix())
    assert result.is_valid is False


def test_histogram_requires_value_role() -> None:
    profile = _sample_profile()
    plan = _chart_plan(
        "histogram",
        [DataRole(role="value", field="Amount")],
        intent="show_distribution",
    )
    result = VisualPlanValidator().validate(plan, profile, _matrix())
    assert result.is_valid is True


def test_box_plot_requires_value_role() -> None:
    profile = _sample_profile()
    plan = _chart_plan(
        "box_plot",
        [DataRole(role="value", field="Amount")],
        intent="show_distribution",
    )
    result = VisualPlanValidator().validate(plan, profile, _matrix())
    assert result.is_valid is True


def test_heatmap_requires_matrix_roles() -> None:
    profile = _sample_profile()
    plan = _chart_plan(
        "heatmap",
        [
            DataRole(role="x_category", field="Region"),
            DataRole(role="y_category", field="Status"),
            DataRole(role="measure", field="Amount", aggregation="sum"),
        ],
        intent="show_matrix",
    )
    result = VisualPlanValidator().validate(plan, profile, _matrix())
    assert result.is_valid is True


def test_stacked_bar_requires_stack_role() -> None:
    profile = _sample_profile()
    plan = _chart_plan(
        "stacked_bar",
        [
            DataRole(role="category", field="Region"),
            DataRole(role="stack", field="Status"),
            DataRole(role="measure", field="Amount", aggregation="sum"),
        ],
        intent="compare_stacked_categories",
    )
    result = VisualPlanValidator().validate(plan, profile, _matrix())
    assert result.is_valid is True


def test_sequence_diagram_passes_when_graph_contract_roles_present() -> None:
    plan = VisualPlan(
        visual_kind="diagram",
        intent="show_process",
        diagram_type="sequence_diagram",
        diagram_nodes=[
            DiagramNode(id="A", label="User"),
            DiagramNode(id="B", label="App"),
        ],
        diagram_edges=[DiagramEdge(source="A", target="B", label="Request")],
    )
    plan.render_target.renderer = "mermaid"
    result = VisualPlanValidator().validate(plan, None, _matrix())
    assert result.is_valid is True


def test_donut_is_rejected_by_graph_matrix() -> None:
    profile = _sample_profile()
    plan = _chart_plan(
        "donut",
        [
            DataRole(role="category", field="Region"),
            DataRole(role="measure", field="Amount", aggregation="sum"),
        ],
    )
    result = VisualPlanValidator().validate(plan, profile, _matrix())
    assert result.is_valid is False
