"""Plotly trace and layout builders for individual chart types."""

from __future__ import annotations

import pandas as pd

from semantic_visual_builder.planning.visual_plan import get_role
from semantic_visual_builder.planning.visual_plan_schema import VisualPlan
from semantic_visual_builder.renderers.plotly_3d import (  # noqa: F401
    apply_3d_to_layout,
    bar3d_trace,
    chart_style,
    extrusion_marker,
    scene,
)


class PlotlyChartBuilders:
    """Build Plotly trace+layout dicts for each supported chart type."""

    def build_area(
        self, plan: VisualPlan, dataframe: pd.DataFrame
    ) -> tuple[list[dict], dict, list[str]]:
        x_values, y_values, x_title, y_title = self._aggregate_xy(plan, dataframe)
        style = chart_style(plan)
        if style == "true_3d":
            trace = {
                "type": "scatter3d",
                "mode": "lines",
                "fill": "toself",
                "x": list(range(len(x_values))),
                "y": y_values,
                "z": [0.0] * len(x_values),
                "name": y_title,
                "line": {"width": 6},
            }
        else:
            trace = {
                "type": "scatter",
                "mode": "lines",
                "fill": "tozeroy",
                "x": x_values,
                "y": y_values,
                "name": y_title,
            }
            if style == "soft_3d":
                trace["marker"] = extrusion_marker(plan)
        layout = self._layout(plan, x_title=x_title, y_title=y_title)
        apply_3d_to_layout(plan, layout)
        return [trace], layout, []

    def build_stacked_area(
        self, plan: VisualPlan, dataframe: pd.DataFrame
    ) -> tuple[list[dict], dict, list[str]]:
        x_role = get_role(plan, "x")
        stack_role = get_role(plan, "stack") or get_role(plan, "series")
        measure_role = get_role(plan, "measure")
        if x_role is None or stack_role is None or measure_role is None:
            raise ValueError("Stacked area requires x, stack, and measure roles.")
        x_field = x_role.field
        stack_field = stack_role.field
        if x_field is None or stack_field is None:
            raise ValueError("Stacked area roles require fields.")
        grouped = self._group_measure(
            dataframe, [x_field, stack_field], measure_role, transform=x_role.transform
        )
        x_col = "_x"
        stack_col = stack_field
        value_col = "_val"
        x_values = sorted(grouped[x_col].astype(str).unique().tolist())
        stacks = sorted(grouped[stack_col].astype(str).unique().tolist())
        traces: list[dict] = []
        style = chart_style(plan)
        if style == "true_3d":
            # Surface plot per stack level.
            for index, stack_value in enumerate(stacks):
                subset = grouped[grouped[stack_col].astype(str) == stack_value].set_index(x_col)
                y_vals = [
                    float(subset.loc[x, value_col]) if x in subset.index else 0.0
                    for x in x_values
                ]
                traces.append({
                    "type": "scatter3d",
                    "mode": "lines",
                    "x": list(range(len(x_values))),
                    "y": y_vals,
                    "z": [index] * len(x_values),
                    "name": stack_value,
                    "line": {"width": 6},
                })
        else:
            for stack_value in stacks:
                subset = grouped[grouped[stack_col].astype(str) == stack_value].set_index(x_col)
                y_vals = [
                    float(subset.loc[x, value_col]) if x in subset.index else 0.0
                    for x in x_values
                ]
                trace: dict = {
                    "type": "scatter",
                    "mode": "lines",
                    "stackgroup": "one",
                    "x": x_values,
                    "y": y_vals,
                    "name": stack_value,
                }
                if style == "soft_3d":
                    trace["fill"] = "tonexty"
                    trace["line"] = {"shape": "spline"}
                traces.append(trace)
        layout = self._layout(
            plan,
            x_title=x_field or "X",
            y_title=measure_role.field or "Value",
        )
        apply_3d_to_layout(plan, layout)
        return traces, layout, []

    def build_bubble(
        self, plan: VisualPlan, dataframe: pd.DataFrame
    ) -> tuple[list[dict], dict, list[str]]:
        x_role = get_role(plan, "x")
        y_role = get_role(plan, "y")
        size_role = get_role(plan, "size")
        if x_role is None or y_role is None or size_role is None:
            raise ValueError("Bubble chart requires x, y, and size roles.")
        x_values = pd.to_numeric(dataframe[x_role.field], errors="coerce")
        y_values = pd.to_numeric(dataframe[y_role.field], errors="coerce")
        size_values = pd.to_numeric(dataframe[size_role.field], errors="coerce")
        valid = ~(x_values.isna() | y_values.isna() | size_values.isna())
        sizes = size_values[valid]
        if chart_style(plan) == "true_3d":
            sizeref = max(float(sizes.max()) / 40.0, 1.0) if not sizes.empty else 1.0
            trace = {
                "type": "scatter3d",
                "mode": "markers",
                "x": x_values[valid].tolist(),
                "y": y_values[valid].tolist(),
                "z": sizes.tolist(),
                "name": size_role.field or "Size",
                "marker": {
                    "size": sizes.tolist(),
                    "sizemode": "area",
                    "sizeref": sizeref,
                    "opacity": 0.9,
                    "line": {"width": 0},
                },
            }
        else:
            sizeref = max(float(sizes.max()) / 40.0, 1.0) if not sizes.empty else 1.0
            trace = {
                "type": "scatter",
                "mode": "markers",
                "x": x_values[valid].tolist(),
                "y": y_values[valid].tolist(),
                "name": size_role.field or "Size",
                "marker": {
                    "size": sizes.tolist(),
                    "sizemode": "area",
                    "sizeref": sizeref,
                },
            }
            if chart_style(plan) == "soft_3d":
                trace["marker"].update(extrusion_marker(plan))
        layout = self._layout(plan, x_title=x_role.field or "X", y_title=y_role.field or "Y")
        apply_3d_to_layout(plan, layout)
        return [trace], layout, []

    def build_treemap(
        self, plan: VisualPlan, dataframe: pd.DataFrame
    ) -> tuple[list[dict], dict, list[str]]:
        category_role = get_role(plan, "category")
        measure_role = get_role(plan, "measure")
        if category_role is None or measure_role is None:
            raise ValueError("Treemap requires category and measure roles.")
        grouped = self._aggregate_category(dataframe, category_role.field, measure_role)
        if chart_style(plan) == "true_3d":
            trace = {
                "type": "mesh3d",
                "x": list(range(len(grouped))),
                "y": grouped["value"].tolist(),
                "z": [0] * len(grouped),
                "intensity": grouped["value"].tolist(),
                "text": grouped["label"].tolist(),
                "name": measure_role.field or "Value",
            }
        elif chart_style(plan) == "soft_3d":
            trace = {
                "type": "treemap",
                "labels": grouped["label"].tolist(),
                "parents": ["" for _ in grouped["label"].tolist()],
                "values": grouped["value"].tolist(),
                "marker": {"line": {"width": 2, "color": "#ffffff"}},
            }
        else:
            trace = {
                "type": "treemap",
                "labels": grouped["label"].tolist(),
                "parents": ["" for _ in grouped["label"].tolist()],
                "values": grouped["value"].tolist(),
            }
        layout = self._layout(plan, x_title="", y_title="")
        apply_3d_to_layout(plan, layout)
        return [trace], layout, []

    def build_waterfall(
        self, plan: VisualPlan, dataframe: pd.DataFrame
    ) -> tuple[list[dict], dict, list[str]]:
        category_role = get_role(plan, "category")
        measure_role = get_role(plan, "measure")
        if category_role is None or measure_role is None:
            raise ValueError("Waterfall requires category and measure roles.")
        grouped = self._aggregate_category(dataframe, category_role.field, measure_role)
        labels = grouped["label"].tolist()
        values = grouped["value"].tolist()
        if chart_style(plan) == "true_3d":
            trace = {
                "type": "bar3d",
                "x": labels,
                "y": list(range(len(labels))),
                "z": [0] * len(labels),
                "dz": [float(v) for v in values],
                "marker": {"color": values},
                "name": measure_role.field or "Value",
            }
        else:
            trace = {
                "type": "waterfall",
                "x": labels,
                "y": values,
                "measure": ["relative" for _ in values],
            }
            if chart_style(plan) == "soft_3d":
                trace.setdefault("connector", {"line": {"width": 2}})
                trace.setdefault("increasing", {"marker": {"line": {"width": 2}}})
                trace.setdefault("decreasing", {"marker": {"line": {"width": 2}}})
        layout = self._layout(plan, x_title=category_role.field or "Category", y_title=measure_role.field or "Value")
        apply_3d_to_layout(plan, layout)
        return [trace], layout, []

    def build_funnel(
        self, plan: VisualPlan, dataframe: pd.DataFrame
    ) -> tuple[list[dict], dict, list[str]]:
        category_role = get_role(plan, "category")
        measure_role = get_role(plan, "measure")
        if category_role is None or measure_role is None:
            raise ValueError("Funnel requires category and measure roles.")
        grouped = self._aggregate_category(dataframe, category_role.field, measure_role)
        labels = grouped["label"].tolist()
        values = grouped["value"].tolist()
        if chart_style(plan) == "true_3d":
            trace = {
                "type": "funnel3d" if False else "scatter3d",  # funnel3d needs custom; use scatter3d steps
                "x": list(range(len(labels))),
                "y": values,
                "z": values,
                "mode": "lines+markers",
                "line": {"width": 12, "shape": "spline"},
                "marker": {"size": 8},
                "name": measure_role.field or "Value",
            }
        else:
            trace = {
                "type": "funnel",
                "y": labels,
                "x": values,
            }
            if chart_style(plan) == "soft_3d":
                trace["textposition"] = "inside"
                trace["textinfo"] = "value+percent initial"
        layout = self._layout(plan, x_title=measure_role.field or "Value", y_title=category_role.field or "Stage")
        apply_3d_to_layout(plan, layout)
        return [trace], layout, []

    def build_radar(
        self, plan: VisualPlan, dataframe: pd.DataFrame
    ) -> tuple[list[dict], dict, list[str]]:
        category_role = get_role(plan, "category")
        measure_role = get_role(plan, "measure")
        if category_role is None or measure_role is None:
            raise ValueError("Radar requires category and measure roles.")
        grouped = self._aggregate_category(dataframe, category_role.field, measure_role)
        theta = grouped["label"].tolist()
        r_values = grouped["value"].tolist()
        if theta:
            theta.append(theta[0])
            r_values.append(r_values[0])
        if chart_style(plan) == "true_3d":
            trace = {
                "type": "scatter3d",
                "mode": "lines+markers",
                "x": r_values,
                "y": [i for i in range(len(theta))],
                "z": [0.0] * len(theta),
                "name": measure_role.field or "Value",
                "line": {"width": 6},
            }
            layout = self._layout(plan, x_title="", y_title="")
            layout["scene"] = scene(plan)
            return [trace], layout, []
        trace = {
            "type": "scatterpolar",
            "r": r_values,
            "theta": theta,
            "fill": "toself",
            "name": measure_role.field or "Value",
        }
        if chart_style(plan) == "soft_3d":
            trace["marker"] = {"size": 12, **extrusion_marker(plan)}
        layout = self._layout(plan, x_title="", y_title="")
        layout["polar"] = {"radialaxis": {"visible": True}}
        apply_3d_to_layout(plan, layout)
        return [trace], layout, []

    def build_gauge(
        self, plan: VisualPlan, dataframe: pd.DataFrame
    ) -> tuple[list[dict], dict, list[str]]:
        measure_role = get_role(plan, "measure")
        if measure_role is None:
            raise ValueError("Gauge requires a measure role.")
        value = self._aggregate_single_value(dataframe, measure_role)
        max_value = max(value, 1.0)
        gauge = {"axis": {"range": [0, max_value]}}
        if chart_style(plan) == "soft_3d":
            gauge["bar"] = {"color": "#1f4e79", "thickness": 0.35}
        elif chart_style(plan) == "true_3d":
            gauge["bar"] = {"color": "#1f4e79", "thickness": 0.5}
            gauge["steps"] = [
                {"range": [0, max_value * 0.5], "color": "#dbeafe"},
                {"range": [max_value * 0.5, max_value], "color": "#bfdbfe"},
            ]
        trace = {
            "type": "indicator",
            "mode": "gauge+number",
            "value": value,
            "title": {"text": plan.style.title or (measure_role.field or "Value")},
            "gauge": gauge,
        }
        return [trace], self._layout(plan, x_title="", y_title=""), []

    def build_kpi_card(
        self, plan: VisualPlan, dataframe: pd.DataFrame
    ) -> tuple[list[dict], dict, list[str]]:
        measure_role = get_role(plan, "measure")
        if measure_role is None:
            raise ValueError("KPI card requires a measure role.")
        value = self._aggregate_single_value(dataframe, measure_role)
        trace = {
            "type": "indicator",
            "mode": "number",
            "value": value,
            "title": {"text": plan.style.title or (measure_role.field or "Value")},
        }
        return [trace], self._layout(plan, x_title="", y_title=""), []

    def build_histogram(
        self, plan: VisualPlan, dataframe: pd.DataFrame
    ) -> tuple[list[dict], dict, list[str]]:
        value_role = get_role(plan, "value")
        if value_role is None or value_role.field is None:
            raise ValueError("Histogram requires a 'value' role with a field.")
        series = pd.to_numeric(dataframe[value_role.field], errors="coerce").dropna()
        if chart_style(plan) == "true_3d":
            counts, edges = pd.cut(series, bins=20, retbins=True)
            counts = counts.value_counts().sort_index()
            values = counts.tolist()
            labels = [str(idx) for idx in counts.index.tolist()]
            trace = bar3d_trace(
                plan,
                labels,
                values,
                name=value_role.field,
            )
        else:
            trace = {
                "type": "histogram",
                "x": series.tolist(),
                "name": value_role.field,
            }
            if chart_style(plan) == "soft_3d":
                trace["marker"] = extrusion_marker(plan)
        layout = self._layout(plan, x_title=value_role.field, y_title="Count")
        apply_3d_to_layout(plan, layout)
        return [trace], layout, []

    def build_box_plot(
        self, plan: VisualPlan, dataframe: pd.DataFrame
    ) -> tuple[list[dict], dict, list[str]]:
        value_role = get_role(plan, "value")
        if value_role is None or value_role.field is None:
            raise ValueError("Box plot requires a 'value' role with a field.")
        category_role = get_role(plan, "category")
        series = pd.to_numeric(dataframe[value_role.field], errors="coerce")
        style = chart_style(plan)
        if style == "true_3d":
            if category_role and category_role.field:
                categories = sorted(dataframe[category_role.field].astype(str).unique().tolist())
                traces: list[dict] = []
                for index, cat in enumerate(categories):
                    subset = series[dataframe[category_role.field].astype(str) == cat].dropna().tolist()
                    traces.append({
                        "type": "box",
                        "x": subset,
                        "y": [index] * len(subset),
                        "name": cat,
                    })
                layout = self._layout(plan, x_title=value_role.field, y_title=category_role.field)
            else:
                trace = {
                    "type": "box",
                    "x": series.dropna().tolist(),
                    "y": [0] * len(series.dropna().tolist()),
                    "name": value_role.field,
                }
                traces = [trace]
                layout = self._layout(plan, x_title=value_role.field, y_title="")
            apply_3d_to_layout(plan, layout)
            return traces, layout, []
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
        if style == "soft_3d":
            trace.setdefault("marker", extrusion_marker(plan))
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

        style = chart_style(plan)
        if style == "true_3d":
            trace = {
                "type": "surface",
                "x": x_labels,
                "y": y_labels,
                "z": z_values,
                "colorscale": "Blues",
                "contours": {"z": {"show": True, "usecolormap": True, "highlightcolor": "#ffffff"}},
            }
        else:
            trace = {
                "type": "heatmap",
                "x": x_labels,
                "y": y_labels,
                "z": z_values,
                "colorscale": "Blues",
            }
            if style == "soft_3d":
                trace["xgap"] = 2
                trace["ygap"] = 2
        layout = self._layout(plan, x_title=x_field or "X", y_title=y_field or "Y")
        apply_3d_to_layout(plan, layout)
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
        style = chart_style(plan)
        if style == "true_3d":
            for index, sv in enumerate(stack_values):
                subset = grouped[grouped["_stack"].astype(str) == sv].set_index("_cat")
                y_vals = [float(subset.loc[c, "_val"]) if c in subset.index else 0.0 for c in categories]
                traces.append({
                    "type": "bar3d",
                    "x": categories,
                    "y": [index] * len(categories),
                    "z": [0] * len(categories),
                    "dz": y_vals,
                    "name": sv,
                })
            layout = self._layout(plan, x_title=cat_field or "Category", y_title="Stack", z_title=m_field or "Value")
            layout["scene"] = scene(plan)
            return traces, layout, warnings
        for sv in stack_values:
            subset = grouped[grouped["_stack"].astype(str) == sv].set_index("_cat")
            y_vals = [float(subset.loc[c, "_val"]) if c in subset.index else 0.0 for c in categories]
            trace = {
                "type": "bar",
                "x": categories,
                "y": y_vals,
                "name": sv,
            }
            if style == "soft_3d":
                trace["marker"] = extrusion_marker(plan)
            traces.append(trace)

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

    def _aggregate_category(self, dataframe: pd.DataFrame, field: str | None, measure_role) -> pd.DataFrame:
        if field is None:
            raise ValueError("Category field is required.")
        if measure_role.field == "row_count" or measure_role.aggregation == "count":
            grouped = dataframe.groupby(field, dropna=False).size().reset_index(name="value")
        else:
            series = pd.to_numeric(dataframe[measure_role.field], errors="coerce")
            grouped = (
                dataframe.assign(_measure=series)
                .groupby(field, dropna=False)["_measure"]
                .sum()
                .reset_index(name="value")
            )
        grouped = grouped.sort_values("value", ascending=False).rename(columns={field: "label"})
        return grouped

    def _aggregate_xy(
        self, plan: VisualPlan, dataframe: pd.DataFrame
    ) -> tuple[list[str], list[float], str, str]:
        x_role = get_role(plan, "x")
        y_role = get_role(plan, "y")
        if x_role is None or y_role is None or x_role.field is None:
            raise ValueError("Chart requires x and y roles with fields.")
        grouped = self._group_measure(
            dataframe, [x_role.field], y_role, transform=x_role.transform
        )
        return (
            grouped["_x"].astype(str).tolist(),
            grouped["_val"].astype(float).tolist(),
            x_role.field,
            y_role.field or "Value",
        )

    def _group_measure(
        self,
        dataframe: pd.DataFrame,
        fields: list[str],
        measure_role,
        transform: str | None = None,
    ) -> pd.DataFrame:
        working = dataframe.copy()
        group_fields: list[str] = []
        for field in fields:
            if transform and field == fields[0]:
                series = pd.to_datetime(working[field], errors="coerce")
                if transform == "week":
                    working["_x"] = series.dt.strftime("%G-W%V")
                elif transform == "month":
                    working["_x"] = series.dt.to_period("M").astype(str)
                elif transform == "year":
                    working["_x"] = series.dt.to_period("Y").astype(str)
                else:
                    working["_x"] = series.dt.to_period("D").astype(str)
                group_fields.append("_x")
            else:
                group_fields.append(field)
        if measure_role.field == "row_count" or measure_role.aggregation == "count":
            grouped = (
                working.groupby(group_fields, dropna=False)
                .size()
                .reset_index(name="_val")
            )
        else:
            series = pd.to_numeric(working[measure_role.field], errors="coerce")
            grouped = (
                working.assign(_measure=series)
                .groupby(group_fields, dropna=False)["_measure"]
                .sum()
                .reset_index(name="_val")
            )
        return grouped.sort_values(group_fields)

    def _aggregate_single_value(self, dataframe: pd.DataFrame, measure_role) -> float:
        if measure_role.field == "row_count" or measure_role.aggregation == "count":
            return float(len(dataframe))
        series = pd.to_numeric(dataframe[measure_role.field], errors="coerce")
        aggregation = (measure_role.aggregation or "sum").lower()
        if aggregation in {"avg", "mean"}:
            return float(series.mean(skipna=True) or 0.0)
        if aggregation == "min":
            return float(series.min(skipna=True) or 0.0)
        if aggregation == "max":
            return float(series.max(skipna=True) or 0.0)
        if aggregation == "median":
            return float(series.median(skipna=True) or 0.0)
        return float(series.sum(skipna=True) or 0.0)

    def _layout(self, plan: VisualPlan, x_title: str, y_title: str) -> dict:
        title = plan.style.title or self._default_title(plan)
        if plan.style.subtitle:
            title = f"{title} - {plan.style.subtitle}"
        layout: dict = {
            "title": title,
            "xaxis": {"title": x_title},
            "yaxis": {"title": y_title},
            "template": "plotly_white",
            "margin": {"l": 60, "r": 30, "t": 60, "b": 60},
        }
        if chart_style(plan) == "true_3d":
            layout["template"] = "plotly_dark"
            layout["scene"] = scene(plan)
        return layout

    def _default_title(self, plan: VisualPlan) -> str:
        if plan.chart_type == "histogram":
            return "Distribution"
        if plan.chart_type == "box_plot":
            return "Spread"
        if plan.chart_type == "heatmap":
            return "Heatmap"
        if plan.chart_type == "stacked_bar":
            return "Stacked Comparison"
        if plan.chart_type == "area":
            return "Area Trend"
        if plan.chart_type == "stacked_area":
            return "Stacked Area Trend"
        if plan.chart_type == "bubble":
            return "Bubble Chart"
        if plan.chart_type == "treemap":
            return "Treemap"
        if plan.chart_type == "waterfall":
            return "Waterfall"
        if plan.chart_type == "funnel":
            return "Funnel"
        if plan.chart_type == "radar":
            return "Radar"
        if plan.chart_type == "gauge":
            return "Gauge"
        if plan.chart_type == "kpi_card":
            return "KPI"
        return "Visual Preview"
