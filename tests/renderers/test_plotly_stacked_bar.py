"""Tests for PlotlyChartBuilders.build_stacked_bar."""

from __future__ import annotations

import pandas as pd
import pytest

from semantic_visual_builder.planning.visual_plan_schema import DataRole, VisualPlan
from semantic_visual_builder.renderers.plotly_chart_builders import PlotlyChartBuilders


def _plan(cat_field: str, stack_field: str, measure_field: str, aggregation: str = "sum") -> VisualPlan:
    plan = VisualPlan(chart_type="stacked_bar", visual_kind="chart", intent="comparison")
    plan.data_roles = [
        DataRole(role="category", field=cat_field),
        DataRole(role="stack", field=stack_field),
        DataRole(role="measure", field=measure_field, aggregation=aggregation),
    ]
    return plan


class TestStackedBar:
    def test_multiple_traces_per_stack_group(self) -> None:
        df = pd.DataFrame({
            "region": ["East", "West", "East", "West"],
            "product": ["A", "A", "B", "B"],
            "sales": [100.0, 200.0, 150.0, 250.0],
        })
        plan = _plan("region", "product", "sales")
        traces, _, _ = PlotlyChartBuilders().build_stacked_bar(plan, df)
        assert len(traces) == 2

    def test_barmode_is_stack(self) -> None:
        df = pd.DataFrame({"r": ["E", "W"], "p": ["A", "B"], "s": [1.0, 2.0]})
        _, layout, _ = PlotlyChartBuilders().build_stacked_bar(_plan("r", "p", "s"), df)
        assert layout["barmode"] == "stack"

    def test_trace_type_bar(self) -> None:
        df = pd.DataFrame({"r": ["E", "W"], "p": ["A", "B"], "s": [1.0, 2.0]})
        traces, _, _ = PlotlyChartBuilders().build_stacked_bar(_plan("r", "p", "s"), df)
        assert all(t["type"] == "bar" for t in traces)

    def test_missing_roles_raises(self) -> None:
        df = pd.DataFrame({"a": [1], "b": [2]})
        plan = VisualPlan(chart_type="stacked_bar", visual_kind="chart", intent="comparison")
        with pytest.raises(ValueError, match="category"):
            PlotlyChartBuilders().build_stacked_bar(plan, df)

    def test_many_stack_groups_warning(self) -> None:
        regions = ["R"] * 44
        products = [f"P{i}" for i in range(11)] * 4
        sales = [1.0] * 44
        df = pd.DataFrame({"region": regions, "product": products[:44], "sales": sales})
        _, _, warnings = PlotlyChartBuilders().build_stacked_bar(_plan("region", "product", "sales"), df)
        assert any("stack" in w.lower() or "many" in w.lower() for w in warnings)

    def test_categories_are_x_axis(self) -> None:
        df = pd.DataFrame({
            "region": ["East", "West", "East"],
            "product": ["A", "A", "B"],
            "sales": [100.0, 200.0, 150.0],
        })
        plan = _plan("region", "product", "sales")
        traces, _, _ = PlotlyChartBuilders().build_stacked_bar(plan, df)
        all_x = {x for t in traces for x in t["x"]}
        assert all_x == {"East", "West"}

    def test_count_aggregation(self) -> None:
        df = pd.DataFrame({"region": ["E", "E", "W"], "product": ["A", "B", "A"], "sales": [1, 1, 1]})
        plan = VisualPlan(chart_type="stacked_bar", visual_kind="chart", intent="comparison")
        plan.data_roles = [DataRole(role="category", field="region"), DataRole(role="stack", field="product"), DataRole(role="measure", field="row_count", aggregation="count")]
        traces, _, _ = PlotlyChartBuilders().build_stacked_bar(plan, df)
        assert len(traces) >= 1
