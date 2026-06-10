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

        if plan.style.orientation and plan.style.orientation not in {"vertical", "horizontal"}:
            result.add_error("style.orientation must be vertical or horizontal.")
        if plan.style.orientation == "horizontal" and plan.chart_type == "bar":
            result.add_warning("horizontal orientation should usually use horizontal_bar.")
        if plan.chart_type == "horizontal_bar" and plan.style.orientation is None:
            result.add_warning("horizontal_bar charts should declare style.orientation = horizontal.")

    def _validate_diagram(self, plan: VisualPlan, result: ValidationResult) -> None:
        if not plan.diagram_nodes:
            result.add_error("diagram plans must include diagram_nodes.")
        if not plan.diagram_edges:
            result.add_error("diagram plans must include diagram_edges.")

        known_nodes = {node.id for node in plan.diagram_nodes}
        if len(known_nodes) != len(plan.diagram_nodes):
            result.add_error("diagram node ids must be unique.")
        for node in plan.diagram_nodes:
            if not node.id.strip():
                result.add_error("diagram node ids must not be blank.")
            if not node.label.strip():
                result.add_error("diagram node labels must not be blank.")
            if node.node_type not in {"process", "decision", "start", "end"}:
                result.add_warning(f"diagram node type '{node.node_type}' is not standard.")
        for edge in plan.diagram_edges:
            if edge.source not in known_nodes:
                result.add_error(f"diagram edge source '{edge.source}' does not exist.")
            if edge.target not in known_nodes:
                result.add_error(f"diagram edge target '{edge.target}' does not exist.")
            if edge.label and edge.label not in {"Yes", "No"}:
                result.add_warning(f"diagram edge label '{edge.label}' may not be supported by all renderers.")
