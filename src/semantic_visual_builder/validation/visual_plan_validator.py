"""Deterministic visual plan validation."""

from __future__ import annotations

from semantic_visual_builder.data.data_profiler import DatasetProfile
from semantic_visual_builder.knowledge.graph_matrix import GraphMatrix
from semantic_visual_builder.planning.visual_plan import get_role
from semantic_visual_builder.planning.visual_plan_schema import VisualPlan

from .validation_result import ValidationResult


class VisualPlanValidator:
    """Validate a neutral visual plan against deterministic rules."""

    def validate(
        self,
        plan: VisualPlan,
        dataset_profile: DatasetProfile | None = None,
        graph_matrix: GraphMatrix | None = None,
    ) -> ValidationResult:
        result = ValidationResult()
        if plan.visual_kind not in {"chart", "diagram"}:
            result.add_error("visual_kind must be chart or diagram.")
        if not plan.intent.strip():
            result.add_error("intent must not be blank.")
        if plan.visual_kind == "chart" and not plan.chart_type:
            result.add_error("chart plans must have chart_type.")
        if plan.visual_kind == "diagram" and not plan.diagram_type:
            result.add_error("diagram plans must have diagram_type.")

        if plan.visual_kind == "chart":
            self._validate_chart(plan, dataset_profile, result)
        if plan.visual_kind == "diagram":
            self._validate_diagram(plan, result)
        return result

    def _validate_chart(self, plan: VisualPlan, dataset_profile: DatasetProfile | None, result: ValidationResult) -> None:
        x_role = get_role(plan, "x") or get_role(plan, "category") or get_role(plan, "time_or_order")
        y_role = get_role(plan, "y") or get_role(plan, "measure")

        if x_role is None:
            result.add_error("chart plans need an x, category, or time_or_order role.")
        if y_role is None:
            result.add_error("chart plans need a y or measure role.")

        available_fields = {column.name: column.semantic_type for column in dataset_profile.columns} if dataset_profile else {}

        def field_is_numeric(field: str | None) -> bool:
            return bool(field and available_fields.get(field) == "numeric")

        def field_is_datetime(field: str | None) -> bool:
            return bool(field and available_fields.get(field) == "datetime")

        if x_role and x_role.field and x_role.field != "row_count" and x_role.field not in available_fields:
            result.add_error(f"x role field '{x_role.field}' does not exist in the dataset.")
        if y_role and y_role.field and y_role.field != "row_count" and y_role.field not in available_fields:
            result.add_error(f"y role field '{y_role.field}' does not exist in the dataset.")

        if plan.chart_type == "line" and x_role and not (field_is_datetime(x_role.field) or (x_role.transform in {"week", "month", "day", "year"})):
            result.add_warning("line charts work best with a date or ordered x role.")
        if plan.chart_type == "scatter":
            if not field_is_numeric(x_role.field if x_role else None):
                result.add_error("scatter charts require numeric x.")
            if not field_is_numeric(y_role.field if y_role else None):
                result.add_error("scatter charts require numeric y.")
        if plan.chart_type == "pie":
            if y_role and y_role.aggregation != "count" and not field_is_numeric(y_role.field):
                result.add_error("pie charts need a numeric or counted measure.")
            if dataset_profile and len(dataset_profile.columns) > 6:
                result.add_warning("pie charts should avoid too many categories.")
        if y_role and y_role.field == "row_count" and y_role.aggregation != "count":
            result.add_error("row_count must use count aggregation.")

    def _validate_diagram(self, plan: VisualPlan, result: ValidationResult) -> None:
        if plan.diagram_type == "flowchart":
            result.add_warning("Diagram extraction starts in a later sprint; current plan is neutral only.")
        elif plan.diagram_type == "sequence_diagram":
            result.add_warning("Diagram extraction starts in a later sprint; current plan is neutral only.")
        else:
            result.add_warning("Diagram extraction starts in a later sprint; current plan is neutral only.")
