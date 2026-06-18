"""Plotly renderer implementation."""

from __future__ import annotations

import json

import pandas as pd

from semantic_visual_builder.data.dataset_context import DatasetContext
from semantic_visual_builder.planning.visual_plan import get_role
from semantic_visual_builder.planning.visual_plan_schema import VisualPlan
from semantic_visual_builder.renderers.base_renderer import BaseRenderer
from semantic_visual_builder.renderers.plotly_style_adapter import PlotlyStyleAdapter
from semantic_visual_builder.renderers.renderer_result import RendererOutput
from semantic_visual_builder.validation.validation_result import ValidationResult

_SUPPORTED_CHART_TYPES = {
    "bar", "horizontal_bar", "line", "area", "stacked_area", "scatter",
    "bubble", "pie", "donut", "stacked_bar", "histogram", "box_plot",
    "heatmap", "treemap", "waterfall", "funnel", "radar", "gauge",
    "kpi_card",
}

_DEFAULT_CATEGORICAL_SEQUENCE = [
    "#4C78A8",
    "#F58518",
    "#E45756",
    "#72B7B2",
    "#54A24B",
    "#EECA3B",
    "#B279A2",
    "#FF9DA6",
    "#9D755D",
    "#BAB0AC",
]


class PlotlyRenderer(BaseRenderer):
    """Render chart plans to Plotly JSON."""

    name = "plotly"

    def __init__(self) -> None:
        self.style_adapter = PlotlyStyleAdapter()

    def can_render(self, visual_plan: VisualPlan) -> bool:
        return visual_plan.visual_kind == "chart" and visual_plan.chart_type in _SUPPORTED_CHART_TYPES

    def render(
        self,
        visual_plan: VisualPlan,
        dataset_context: DatasetContext | None = None,
    ) -> RendererOutput:
        if not self.can_render(visual_plan):
            raise ValueError("PlotlyRenderer can only render supported chart plans.")
        if dataset_context is None or dataset_context.loaded_dataset is None:
            raise ValueError("PlotlyRenderer requires a loaded dataset.")
        dataframe = dataset_context.loaded_dataset.dataframe.copy()
        traces, layout, warnings = self._build_chart_multi(visual_plan, dataframe)
        config = {"data": traces, "layout": layout}
        config = self.style_adapter.apply_style_to_config(config, visual_plan)
        content = json.dumps(config, ensure_ascii=False)
        metadata = {
            "warnings": warnings,
            "style_profile_id": visual_plan.metadata.style_profile_id,
            "style_profile_name": visual_plan.metadata.style_profile_name,
        }
        return RendererOutput(renderer_name=self.name, output_type="plotly_json", content=content, metadata=metadata)

    def validate_output(self, output: RendererOutput) -> ValidationResult:
        result = ValidationResult()
        if output.output_type != "plotly_json":
            result.add_error("output_type must be plotly_json.")
            return result
        try:
            payload = json.loads(output.content)
        except json.JSONDecodeError as exc:
            result.add_error(f"Plotly output must be valid JSON: {exc.msg}")
            return result
        if "data" not in payload or "layout" not in payload:
            result.add_error("Plotly JSON must have data and layout keys.")
        if not isinstance(payload.get("data"), list):
            result.add_error("Plotly JSON data must be a list.")
        if not isinstance(payload.get("layout"), dict):
            result.add_error("Plotly JSON layout must be an object.")
        return result

    def _build_chart_multi(
        self, plan: VisualPlan, dataframe: pd.DataFrame
    ) -> tuple[list[dict[str, object]], dict[str, object], list[str]]:
        from semantic_visual_builder.renderers.plotly_chart_builders import (
            PlotlyChartBuilders,
        )
        chart_type = plan.chart_type or "bar"
        builders = PlotlyChartBuilders()
        if chart_type == "histogram":
            return builders.build_histogram(plan, dataframe)
        if chart_type == "box_plot":
            return builders.build_box_plot(plan, dataframe)
        if chart_type == "heatmap":
            return builders.build_heatmap(plan, dataframe)
        if chart_type == "stacked_bar":
            return builders.build_stacked_bar(plan, dataframe)
        if chart_type == "area":
            return builders.build_area(plan, dataframe)
        if chart_type == "stacked_area":
            return builders.build_stacked_area(plan, dataframe)
        if chart_type == "bubble":
            return builders.build_bubble(plan, dataframe)
        if chart_type == "treemap":
            return builders.build_treemap(plan, dataframe)
        if chart_type == "waterfall":
            return builders.build_waterfall(plan, dataframe)
        if chart_type == "funnel":
            return builders.build_funnel(plan, dataframe)
        if chart_type == "radar":
            return builders.build_radar(plan, dataframe)
        if chart_type == "gauge":
            return builders.build_gauge(plan, dataframe)
        if chart_type == "kpi_card":
            return builders.build_kpi_card(plan, dataframe)
        trace, layout, warnings = self._build_chart(plan, dataframe)
        return [trace], layout, warnings

    def _build_chart(self, plan: VisualPlan, dataframe: pd.DataFrame) -> tuple[dict[str, object], dict[str, object], list[str]]:
        chart_type = plan.chart_type or "bar"
        if chart_type == "line":
            return self._build_line(plan, dataframe)
        if chart_type == "horizontal_bar":
            return self._build_bar(plan, dataframe, horizontal=True)
        if chart_type == "scatter":
            return self._build_scatter(plan, dataframe)
        if chart_type == "pie":
            return self._build_pie(plan, dataframe)
        if chart_type == "donut":
            return self._build_pie(plan, dataframe, hole=0.45)
        return self._build_bar(plan, dataframe, horizontal=False)

    def _build_line(self, plan: VisualPlan, dataframe: pd.DataFrame) -> tuple[dict[str, object], dict[str, object], list[str]]:
        x_role = get_role(plan, "x")
        y_role = get_role(plan, "y")
        if x_role is None or y_role is None:
            raise ValueError("Line charts require x and y roles.")
        series = pd.to_datetime(dataframe[x_role.field], errors="coerce")
        transform = (x_role.transform or "").lower()
        if transform == "week":
            grouped = dataframe.assign(_x=series.dt.strftime("%G-W%V"))
        elif transform == "month":
            grouped = dataframe.assign(_x=series.dt.to_period("M").astype(str))
        elif transform == "year":
            grouped = dataframe.assign(_x=series.dt.to_period("Y").astype(str))
        else:
            grouped = dataframe.assign(_x=series.dt.to_period("D").astype(str))
        counts = grouped.groupby("_x", dropna=False).size().reset_index(name="_y").sort_values("_x")
        trace = {
            "type": "scatter",
            "mode": "lines+markers",
            "x": counts["_x"].tolist(),
            "y": counts["_y"].tolist(),
            "name": "Transactions",
        }
        primary_colour = self._primary_palette_colour(plan)
        if primary_colour:
            trace["line"] = {"color": primary_colour}
            trace["marker"] = {"color": primary_colour}
        layout_title = "Week" if transform == "week" else "Month" if transform == "month" else "Year" if transform == "year" else (x_role.field or "Time")
        layout = self._layout(plan, x_title=layout_title, y_title="Transactions")
        return trace, layout, []

    def _build_bar(self, plan: VisualPlan, dataframe: pd.DataFrame, horizontal: bool) -> tuple[dict[str, object], dict[str, object], list[str]]:
        category = get_role(plan, "category")
        measure = get_role(plan, "measure")
        if category is None or measure is None:
            raise ValueError("Bar charts require category and measure roles.")
        grouped = self._aggregate_category(dataframe, category.field, measure)
        colors = self._bar_colors(plan, grouped["label"].tolist())
        warnings = self._highlight_warnings(plan, category.field)
        if horizontal:
            trace = {"type": "bar", "orientation": "h", "x": grouped["value"].tolist(), "y": grouped["label"].tolist(), "name": self._measure_name(measure)}
            if colors:
                trace["marker"] = {"color": colors}
            layout = self._layout(plan, x_title=self._measure_name(measure), y_title=category.field or "Category")
        else:
            trace = {"type": "bar", "x": grouped["label"].tolist(), "y": grouped["value"].tolist(), "name": self._measure_name(measure)}
            if colors:
                trace["marker"] = {"color": colors}
            layout = self._layout(plan, x_title=category.field or "Category", y_title=self._measure_name(measure))
        return trace, layout, warnings

    def _build_scatter(self, plan: VisualPlan, dataframe: pd.DataFrame) -> tuple[dict[str, object], dict[str, object], list[str]]:
        x_role = get_role(plan, "x")
        y_role = get_role(plan, "y")
        if x_role is None or y_role is None:
            raise ValueError("Scatter charts require x and y roles.")
        x_values = pd.to_numeric(dataframe[x_role.field], errors="coerce")
        y_values = pd.to_numeric(dataframe[y_role.field], errors="coerce")
        valid = ~(x_values.isna() | y_values.isna())
        trace = {"type": "scatter", "mode": "markers", "x": x_values[valid].tolist(), "y": y_values[valid].tolist(), "name": "Points"}
        color = self._primary_palette_colour(plan) or self._colour_for_scheme(plan.style.colour_scheme)
        if color:
            trace["marker"] = {"color": color}
        layout = self._layout(plan, x_title=x_role.field or "X", y_title=y_role.field or "Y")
        return trace, layout, []

    def _build_pie(self, plan: VisualPlan, dataframe: pd.DataFrame, hole: float = 0.0) -> tuple[dict[str, object], dict[str, object], list[str]]:
        category = get_role(plan, "category")
        measure = get_role(plan, "measure")
        if category is None or measure is None:
            raise ValueError("Pie charts require category and measure roles.")
        grouped = self._aggregate_category(dataframe, category.field, measure)
        trace = {"type": "pie", "labels": grouped["label"].tolist(), "values": grouped["value"].tolist(), "name": self._measure_name(measure)}
        if hole > 0:
            trace["hole"] = hole
        colors = self._categorical_colors(plan, grouped["label"].tolist())
        if colors:
            trace["marker"] = {"colors": colors}
        layout = self._layout(plan, x_title=category.field or "Category", y_title=self._measure_name(measure))
        return trace, layout, self._highlight_warnings(plan, category.field)

    def _aggregate_category(self, dataframe: pd.DataFrame, field: str | None, measure) -> pd.DataFrame:
        if field is None:
            raise ValueError("Category field is required.")
        if measure.field == "row_count" or measure.aggregation == "count":
            grouped = dataframe.groupby(field, dropna=False).size().reset_index(name="value")
        else:
            series = pd.to_numeric(dataframe[measure.field], errors="coerce")
            grouped = dataframe.assign(_measure=series).groupby(field, dropna=False)["_measure"].sum().reset_index(name="value")
        grouped = grouped.sort_values("value", ascending=False).rename(columns={field: "label"})
        return grouped

    def _measure_name(self, measure) -> str:
        if measure.field == "row_count" or measure.aggregation == "count":
            return "Count"
        return measure.field or "Measure"

    def _layout(self, plan: VisualPlan, x_title: str, y_title: str) -> dict[str, object]:
        title = plan.style.title or self._default_title(plan)
        if plan.style.subtitle:
            title = f"{title} - {plan.style.subtitle}"
        x_title = plan.style.labels.get("x", x_title) if plan.style.labels else x_title
        y_title = plan.style.labels.get("y", y_title) if plan.style.labels else y_title
        return {
            "title": title,
            "xaxis": {"title": x_title},
            "yaxis": {"title": y_title},
            "template": "plotly_white",
            "margin": {"l": 60, "r": 30, "t": 60, "b": 60},
        }

    def _bar_colors(self, plan: VisualPlan, labels: list[str]) -> list[str] | None:
        scheme = self._primary_palette_colour(plan) or self._colour_for_scheme(plan.style.colour_scheme)
        highlight = plan.style.highlights or {}
        highlight_value = str(highlight.get("value", "")).lower()
        if not scheme and not highlight_value:
            return None
        base_color = scheme or "#4C78A8"
        highlight_color = "#E45756"
        colors: list[str] = []
        for label in labels:
            if highlight_value and highlight_value in label.lower():
                colors.append(highlight_color)
            else:
                colors.append(base_color)
        return colors

    def _categorical_colors(self, plan: VisualPlan, labels: list[str]) -> list[str] | None:
        palette = plan.style.palette if isinstance(plan.style.palette, dict) else {}
        sequence = palette.get("sequence")
        if isinstance(sequence, list):
            cleaned = [
                str(colour)
                for colour in sequence
                if isinstance(colour, str) and colour
            ]
            if cleaned:
                return [cleaned[index % len(cleaned)] for index, _ in enumerate(labels)]

        primary = self._primary_palette_colour(plan) or self._colour_for_scheme(
            plan.style.colour_scheme
        )
        if primary:
            base_sequence = [primary] + [
                colour for colour in _DEFAULT_CATEGORICAL_SEQUENCE if colour != primary
            ]
        else:
            base_sequence = list(_DEFAULT_CATEGORICAL_SEQUENCE)
        return [base_sequence[index % len(base_sequence)] for index, _ in enumerate(labels)]

    def _primary_palette_colour(self, plan: VisualPlan) -> str | None:
        palette = plan.style.palette if isinstance(plan.style.palette, dict) else {}
        primary = palette.get("primary")
        if isinstance(primary, str) and primary:
            return primary
        sequence = palette.get("sequence")
        if isinstance(sequence, list):
            for colour in sequence:
                if isinstance(colour, str) and colour:
                    return colour
        return None

    def _highlight_warnings(self, plan: VisualPlan, category_field: str | None) -> list[str]:
        highlight = plan.style.highlights or {}
        highlight_field = highlight.get("field")
        if highlight_field and highlight_field != category_field:
            return [f"Highlight field '{highlight_field}' is not part of the rendered visual yet."]
        return []

    def _colour_for_scheme(self, scheme: str | None) -> str | None:
        if not scheme:
            return None
        palette = {
            "blue": "#4C78A8",
            "corporate blue": "#1F4E79",
            "green": "#54A24B",
            "red": "#E45756",
        }
        return palette.get(scheme.lower(), "#4C78A8")

    def _default_title(self, plan: VisualPlan) -> str:
        if plan.intent == "show_trend":
            return "Transactions per Week"
        if plan.intent == "compare_categories":
            return "Category Comparison"
        if plan.intent == "show_relationship":
            return "Relationship"
        return "Visual Preview"
