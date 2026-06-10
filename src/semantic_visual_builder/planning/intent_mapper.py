"""Deterministic user intent mapping."""

from __future__ import annotations

from semantic_visual_builder.data.data_profiler import DatasetProfile
from semantic_visual_builder.knowledge.graph_matrix import GraphMatrix

from .diagram_plan_builder import DiagramPlanBuilder
from .field_mapper import FieldMapper
from .visual_plan import set_role
from .visual_plan_schema import VisualPlan


class IntentMapper:
    """Convert user text into a neutral visual plan draft."""

    def map_request_to_plan(
        self,
        message: str,
        dataset_profile: DatasetProfile | None = None,
        graph_matrix: GraphMatrix | None = None,
    ) -> VisualPlan:
        text = message.lower()
        intent = "unknown"
        visual_kind = "chart"
        chart_type: str | None = None
        diagram_type: str | None = None
        renderer: str | None = None

        if any(marker in text for marker in ("flowchart", "process")):
            intent = "show_process"
            visual_kind = "diagram"
            diagram_type = "flowchart"
            renderer = "mermaid"
        elif "relationship between" in text or "scatter" in text:
            intent = "show_relationship"
            chart_type = "scatter"
            renderer = "plotly"
        elif any(marker in text for marker in ("per week", "per month", "over time")):
            intent = "show_trend"
            chart_type = "line"
            renderer = "plotly"
        elif any(marker in text for marker in ("by region", "by status", "compare")):
            intent = "compare_categories"
            chart_type = "bar"
            renderer = "plotly"

        plan = VisualPlan(
            visual_kind=visual_kind,
            intent=intent,
            chart_type=chart_type,
            diagram_type=diagram_type,
        )
        plan.render_target.renderer = renderer

        if intent == "show_process":
            plan = DiagramPlanBuilder().build_basic_flowchart(message)
            plan.render_target.renderer = "mermaid"

        if dataset_profile is not None:
            plan = FieldMapper().propose_roles(message, dataset_profile, plan)

        if intent == "show_trend" and dataset_profile is not None and not plan.data_roles:
            set_role(plan, "x", dataset_profile.columns[0].name if dataset_profile.columns else None)
            set_role(plan, "y", "row_count", aggregation="count")

        if intent == "compare_categories" and dataset_profile is not None:
            if "amount by region" in text:
                set_role(plan, "category", "Region")
                set_role(plan, "measure", "Amount", aggregation="sum")
            elif "transactions by region" in text:
                set_role(plan, "category", "Region")
                set_role(plan, "measure", "row_count", aggregation="count")

        if graph_matrix is not None and plan.render_target.renderer is None:
            if plan.intent in graph_matrix.list_intents():
                plan.render_target.renderer = "plotly" if plan.visual_kind == "chart" else "mermaid"

        if intent == "unknown":
            plan.notes.append("Intent could not be classified deterministically.")

        return plan
