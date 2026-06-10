"""Plotly trace and layout builders for individual chart types."""

from __future__ import annotations

import pandas as pd

from semantic_visual_builder.planning.visual_plan import get_role
from semantic_visual_builder.planning.visual_plan_schema import VisualPlan


class PlotlyChartBuilders:
    """Build Plotly trace+layout dicts for each supported chart type."""

    def build_histogram(
        self, plan: VisualPlan, dataframe: pd.DataFrame
    ) -> tuple[list[dict], dict, list[str]]:
        value_role = get_role(plan, "value")
        if value_role is None or value_role.field is None:
            raise ValueError("Histogram requires a 'value' role with a field.")
        series = pd.to_numeric(dataframe[value_role.field], errors="coerce").dropna()
        trace = {
            "type": "histogram",
            "x": series.tolist(),
            "name": value_role.field,
        }
        layout = self._layout(plan, x_title=value_role.field, y_title="Count")
        return [trace], layout, []

    def build_box_plot(
        self, plan: VisualPlan, dataframe: pd.DataFrame
    ) -> tuple[list[dict], dict, list[str]]:
        value_role = get_role(plan, "value")
        if value_role is None or value_role.field is None:
            raise ValueError("Box plot requires a 'value' role with a field.")
        category_role = get_role(plan, "category")
        series = pd.to_numeric(dataframe[value_role.field], errors="coerce")

        if category_role and category_role.field:
            cat_values = dataframe[category_role.field].astype(str)
            trace = {
                "type": "box",
                "x": cat_values.tolist(),
                "y": series.tolist(),
                "name": value_role.field,
            }
            layout = self._layout(plan, x_title=category_role.field, y_title=value_role.field)
        else:
            trace = {
                "type": "box",
                "y": series.dropna().tolist(),
                "name": value_role.field,
            }
            layout = self._layout(plan, x_title="", y_title=value_role.field)
        return [trace], layout, []

    def build_heatmap(
        self, plan: VisualPlan, dataframe: pd.DataFrame
    ) -> tuple[list[dict], dict, list[str]]:
        x_role = get_role(plan, "x_category")
        y_role = get_role(plan, "y_category")
        measure_role = get_role(plan, "measure")
        if x_role is None or y_role is None or measure_role is None:
            raise ValueError("Heatmap requires x_category, y_category, and measure roles.")

        x_field = x_role.field
        y_field = y_role.field
        m_field = measure_role.field

        if m_field == "row_count" or measure_role.aggregation == "count":
            pivot = (
                dataframe.groupby([y_field, x_field], dropna=False)
                .size()
                .reset_index(name="_val")
                .pivot(index=y_field, columns=x_field, values="_val")
                .fillna(0)
            )
        else:
            series = pd.to_numeric(dataframe[m_field], errors="coerce")
            pivot = (
                dataframe.assign(_val=series)
                .groupby([y_field, x_field], dropna=False)["_val"]
                .sum()
                .reset_index()
                .pivot(index=y_field, columns=x_field, values="_val")
                .fillna(0)
            )
        x_labels = [str(c) for c in pivot.columns.tolist()]
        y_labels = [str(i) for i in pivot.index.tolist()]
        z_values = pivot.values.tolist()

        warnings: list[str] = []
        if len(x_labels) * len(y_labels) > 200:
            warnings.append("Heatmap has many cells; output may be difficult to read.")

        trace = {
            "type": "heatmap",
            "x": x_labels,
            "y": y_labels,
            "z": z_values,
            "colorscale": "Blues",
        }
        layout = self._layout(plan, x_title=x_field or "X", y_title=y_field or "Y")
        return [trace], layout, warnings

    def build_stacked_bar(
        self, plan: VisualPlan, dataframe: pd.DataFrame
    ) -> tuple[list[dict], dict, list[str]]:
        category_role = get_role(plan, "category")
        stack_role = get_role(plan, "stack")
        measure_role = get_role(plan, "measure")
        if category_role is None or stack_role is None or measure_role is None:
            raise ValueError("Stacked bar requires category, stack, and measure roles.")

        cat_field = category_role.field
        stack_field = stack_role.field
        m_field = measure_role.field

        if m_field == "row_count" or measure_role.aggregation == "count":
            grouped = (
                dataframe.groupby([cat_field, stack_field], dropna=False)
                .size()
                .reset_index(name="_val")
            )
        else:
            series = pd.to_numeric(dataframe[m_field], errors="coerce")
            grouped = (
                dataframe.assign(_val=series)
                .groupby([cat_field, stack_field], dropna=False)["_val"]
                .sum()
                .reset_index()
            )
        grouped.columns = ["_cat", "_stack", "_val"]

        categories = sorted(grouped["_cat"].astype(str).unique().tolist())
        stack_values = sorted(grouped["_stack"].astype(str).unique().tolist())

        warnings: list[str] = []
        if len(stack_values) > 10:
            warnings.append("Many stack groups may produce an unreadable stacked bar chart.")

        traces: list[dict] = []
        for sv in stack_values:
            subset = grouped[grouped["_stack"].astype(str) == sv].set_index("_cat")
            y_vals = [float(subset.loc[c, "_val"]) if c in subset.index else 0.0 for c in categories]
            traces.append({
                "type": "bar",
                "x": categories,
                "y": y_vals,
                "name": sv,
            })

        layout = self._layout(plan, x_title=cat_field or "Category", y_title="Value")
        layout["barmode"] = "stack"
        return traces, layout, warnings

    def build_bar(
        self, plan: VisualPlan, dataframe: pd.DataFrame, horizontal: bool = False
    ) -> tuple[list[dict], dict, list[str]]:
        from semantic_visual_builder.renderers.plotly_renderer import PlotlyRenderer
        renderer = PlotlyRenderer()
        trace, layout, warnings = renderer._build_bar(plan, dataframe, horizontal=horizontal)
        return [trace], layout, warnings

    def build_line(
        self, plan: VisualPlan, dataframe: pd.DataFrame
    ) -> tuple[list[dict], dict, list[str]]:
        from semantic_visual_builder.renderers.plotly_renderer import PlotlyRenderer
        renderer = PlotlyRenderer()
        trace, layout, warnings = renderer._build_line(plan, dataframe)
        return [trace], layout, warnings

    def build_scatter(
        self, plan: VisualPlan, dataframe: pd.DataFrame
    ) -> tuple[list[dict], dict, list[str]]:
        from semantic_visual_builder.renderers.plotly_renderer import PlotlyRenderer
        renderer = PlotlyRenderer()
        trace, layout, warnings = renderer._build_scatter(plan, dataframe)
        return [trace], layout, warnings

    def build_pie(
        self, plan: VisualPlan, dataframe: pd.DataFrame
    ) -> tuple[list[dict], dict, list[str]]:
        from semantic_visual_builder.renderers.plotly_renderer import PlotlyRenderer
        renderer = PlotlyRenderer()
        trace, layout, warnings = renderer._build_pie(plan, dataframe)
        return [trace], layout, warnings

    def _layout(self, plan: VisualPlan, x_title: str, y_title: str) -> dict:
        title = plan.style.title or self._default_title(plan)
        if plan.style.subtitle:
            title = f"{title} - {plan.style.subtitle}"
        return {
            "title": title,
            "xaxis": {"title": x_title},
            "yaxis": {"title": y_title},
            "template": "plotly_white",
            "margin": {"l": 60, "r": 30, "t": 60, "b": 60},
        }

    def _default_title(self, plan: VisualPlan) -> str:
        if plan.chart_type == "histogram":
            return "Distribution"
        if plan.chart_type == "box_plot":
            return "Spread"
        if plan.chart_type == "heatmap":
            return "Heatmap"
        if plan.chart_type == "stacked_bar":
            return "Stacked Comparison"
        return "Visual Preview"
