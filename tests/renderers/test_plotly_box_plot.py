"""Tests for PlotlyChartBuilders.build_box_plot."""

from __future__ import annotations

import pandas as pd
import pytest

from semantic_visual_builder.planning.visual_plan_schema import DataRole, VisualPlan
from semantic_visual_builder.renderers.plotly_chart_builders import PlotlyChartBuilders


def _plan(value_field: str, category_field: str | None = None) -> VisualPlan:
    plan = VisualPlan(chart_type="box_plot", visual_kind="chart", intent="spread")
    plan.data_roles = [DataRole(role="value", field=value_field)]
    if category_field:
        plan.data_roles.append(DataRole(role="category", field=category_field))
    return plan


class TestBoxPlot:
    def test_single_trace(self) -> None:
        df = pd.DataFrame({"score": [10, 20, 30, 40, 50]})
        traces, _, _ = PlotlyChartBuilders().build_box_plot(_plan("score"), df)
        assert len(traces) == 1

    def test_trace_type_box(self) -> None:
        df = pd.DataFrame({"score": [10, 20, 30]})
        traces, _, _ = PlotlyChartBuilders().build_box_plot(_plan("score"), df)
        assert traces[0]["type"] == "box"

    def test_y_values_set_without_category(self) -> None:
        df = pd.DataFrame({"score": [1.0, 2.0, 3.0]})
        traces, _, _ = PlotlyChartBuilders().build_box_plot(_plan("score"), df)
        assert traces[0]["y"] == [1.0, 2.0, 3.0]

    def test_with_category_sets_x(self) -> None:
        df = pd.DataFrame({"score": [10, 20, 30], "group": ["A", "A", "B"]})
        traces, _, _ = PlotlyChartBuilders().build_box_plot(_plan("score", "group"), df)
        assert "x" in traces[0]
        assert set(traces[0]["x"]) == {"A", "B"}

    def test_missing_value_role_raises(self) -> None:
        df = pd.DataFrame({"score": [1, 2, 3]})
        plan = VisualPlan(chart_type="box_plot", visual_kind="chart", intent="spread")
        with pytest.raises(ValueError, match="value"):
            PlotlyChartBuilders().build_box_plot(plan, df)

    def test_no_warnings_returned(self) -> None:
        df = pd.DataFrame({"score": [1, 2, 3]})
        _, _, warnings = PlotlyChartBuilders().build_box_plot(_plan("score"), df)
        assert warnings == []
