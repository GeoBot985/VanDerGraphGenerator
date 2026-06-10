"""Tests for PlotlyChartBuilders.build_heatmap."""

from __future__ import annotations

import pandas as pd
import pytest

from semantic_visual_builder.planning.visual_plan_schema import DataRole, VisualPlan
from semantic_visual_builder.renderers.plotly_chart_builders import PlotlyChartBuilders


def _plan(x_field: str, y_field: str, measure_field: str, aggregation: str = "sum") -> VisualPlan:
    plan = VisualPlan(chart_type="heatmap", visual_kind="chart", intent="matrix")
    plan.data_roles = [
        DataRole(role="x_category", field=x_field),
        DataRole(role="y_category", field=y_field),
        DataRole(role="measure", field=measure_field, aggregation=aggregation),
    ]
    return plan


class TestHeatmap:
    def test_single_trace(self) -> None:
        df = pd.DataFrame({"cat": ["A", "A", "B"], "group": ["X", "Y", "X"], "val": [1.0, 2.0, 3.0]})
        traces, _, _ = PlotlyChartBuilders().build_heatmap(_plan("cat", "group", "val"), df)
        assert len(traces) == 1

    def test_trace_type_heatmap(self) -> None:
        df = pd.DataFrame({"cat": ["A", "B"], "group": ["X", "Y"], "val": [1.0, 2.0]})
        traces, _, _ = PlotlyChartBuilders().build_heatmap(_plan("cat", "group", "val"), df)
        assert traces[0]["type"] == "heatmap"

    def test_z_is_list_of_lists(self) -> None:
        df = pd.DataFrame({"cat": ["A", "B"], "group": ["X", "Y"], "val": [1.0, 2.0]})
        traces, _, _ = PlotlyChartBuilders().build_heatmap(_plan("cat", "group", "val"), df)
        assert isinstance(traces[0]["z"], list)
        assert isinstance(traces[0]["z"][0], list)

    def test_missing_roles_raises(self) -> None:
        df = pd.DataFrame({"a": [1], "b": [2]})
        plan = VisualPlan(chart_type="heatmap", visual_kind="chart", intent="matrix")
        with pytest.raises(ValueError, match="x_category"):
            PlotlyChartBuilders().build_heatmap(plan, df)

    def test_large_heatmap_warning(self) -> None:
        cats = [f"c{i}" for i in range(20)]
        groups = [f"g{j}" for j in range(15)]
        rows = [{"cat": c, "group": g, "val": 1} for c in cats for g in groups]
        df = pd.DataFrame(rows)
        plan = _plan("cat", "group", "val")
        _, _, warnings = PlotlyChartBuilders().build_heatmap(plan, df)
        assert any("cells" in w.lower() or "many" in w.lower() for w in warnings)

    def test_count_aggregation(self) -> None:
        df = pd.DataFrame({"cat": ["A", "A", "B"], "group": ["X", "X", "Y"], "val": [1, 1, 1]})
        plan = VisualPlan(chart_type="heatmap", visual_kind="chart", intent="matrix")
        plan.data_roles = [DataRole(role="x_category", field="cat"), DataRole(role="y_category", field="group"), DataRole(role="measure", field="row_count", aggregation="count")]
        traces, _, _ = PlotlyChartBuilders().build_heatmap(plan, df)
        assert traces[0]["type"] == "heatmap"
