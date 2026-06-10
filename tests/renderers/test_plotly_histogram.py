"""Tests for PlotlyChartBuilders.build_histogram."""

from __future__ import annotations

import pandas as pd
import pytest

from semantic_visual_builder.planning.visual_plan_schema import DataRole, VisualPlan
from semantic_visual_builder.renderers.plotly_chart_builders import PlotlyChartBuilders


def _plan_with_value(field: str) -> VisualPlan:
    plan = VisualPlan(chart_type="histogram", visual_kind="chart", intent="distribution")
    plan.data_roles = [DataRole(role="value", field=field)]
    return plan


class TestHistogram:
    def test_returns_single_trace(self) -> None:
        df = pd.DataFrame({"age": [20, 25, 30, 35, 40]})
        plan = _plan_with_value("age")
        traces, layout, warnings = PlotlyChartBuilders().build_histogram(plan, df)
        assert len(traces) == 1
        assert traces[0]["type"] == "histogram"

    def test_x_values_set(self) -> None:
        df = pd.DataFrame({"age": [20, 25, 30]})
        plan = _plan_with_value("age")
        traces, _, _ = PlotlyChartBuilders().build_histogram(plan, df)
        assert traces[0]["x"] == [20.0, 25.0, 30.0]

    def test_non_numeric_rows_dropped(self) -> None:
        df = pd.DataFrame({"score": [1.0, "N/A", 3.0]})
        plan = _plan_with_value("score")
        traces, _, _ = PlotlyChartBuilders().build_histogram(plan, df)
        assert len(traces[0]["x"]) == 2

    def test_missing_value_role_raises(self) -> None:
        df = pd.DataFrame({"score": [1, 2, 3]})
        plan = VisualPlan(chart_type="histogram", visual_kind="chart", intent="distribution")
        with pytest.raises(ValueError, match="value"):
            PlotlyChartBuilders().build_histogram(plan, df)

    def test_y_title_is_count(self) -> None:
        df = pd.DataFrame({"age": [20, 25, 30]})
        plan = _plan_with_value("age")
        _, layout, _ = PlotlyChartBuilders().build_histogram(plan, df)
        assert layout["yaxis"]["title"] == "Count"

    def test_no_warnings_on_valid_input(self) -> None:
        df = pd.DataFrame({"v": list(range(50))})
        plan = _plan_with_value("v")
        _, _, warnings = PlotlyChartBuilders().build_histogram(plan, df)
        assert warnings == []
