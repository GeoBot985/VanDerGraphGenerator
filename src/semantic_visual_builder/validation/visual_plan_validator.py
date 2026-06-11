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

        if graph_matrix is not None:
            self._validate_against_graph_matrix(plan, graph_matrix, result)

        if plan.visual_kind == "chart":
            self._validate_chart(plan, dataset_profile, result)
        if plan.visual_kind == "diagram":
            self._validate_diagram(plan, result)
        return result

    def _validate_against_graph_matrix(
        self,
        plan: VisualPlan,
        graph_matrix: GraphMatrix,
        result: ValidationResult,
    ) -> None:
        if plan.visual_kind not in graph_matrix.visual_kinds():
            result.add_error(f"Unsupported visual_kind: {plan.visual_kind}.")
            return

        visual_type = (
            plan.chart_type if plan.visual_kind == "chart" else plan.diagram_type
        )
        if visual_type is None:
            return

        spec = graph_matrix.get_visual_spec(visual_type)
        if spec is None:
            result.add_error(f"Unsupported {plan.visual_kind}_type: {visual_type}.")
            return
        if spec.get("visual_kind") != plan.visual_kind:
            result.add_error(
                f"{visual_type} is not a supported {plan.visual_kind} type."
            )

        renderer = plan.render_target.renderer
        if renderer is None:
            result.add_error("render_target.renderer must be set.")
        elif not graph_matrix.renderer_allowed(visual_type, renderer):
            result.add_error(f"Unsupported renderer: {renderer} for {visual_type}.")

        if plan.visual_kind == "chart":
            allowed_aggregations = list(
                dict.fromkeys(
                    graph_matrix.allowed_aggregations()
                    + [
                        str(item)
                        for item in spec.get("allowed_aggregations", [])
                        if isinstance(item, str)
                    ]
                )
            )
            allowed_transforms = list(
                dict.fromkeys(
                    graph_matrix.allowed_transforms()
                    + [
                        str(item)
                        for item in spec.get("allowed_transforms", [])
                        if isinstance(item, str)
                    ]
                )
            )
            allowed_filter_operators = list(
                dict.fromkeys(
                    graph_matrix.allowed_filter_operators()
                    + [
                        str(item)
                        for item in spec.get("allowed_filter_operators", [])
                        if isinstance(item, str)
                    ]
                )
            )
            required_roles = graph_matrix.required_roles_for(visual_type)
            allowed_roles = graph_matrix.allowed_roles_for(visual_type)
            for required_role in required_roles:
                if get_role(plan, required_role) is None:
                    result.add_error(
                        f"{visual_type} plans must include role: {required_role}."
                    )

            if allowed_roles:
                for role in plan.data_roles:
                    if role.role not in allowed_roles:
                        result.add_error(
                            f"Unsupported role for {visual_type}: {role.role}."
                        )

            role_specs = graph_matrix.roles()
            for role in plan.data_roles:
                role_spec = role_specs.get(role.role, {})
                if (
                    role.transform is not None
                    and role.transform not in allowed_transforms
                ):
                    result.add_error(
                        f"Unsupported transform for {role.role}: {role.transform}."
                    )
                allowed_role_transforms = [
                    str(item)
                    for item in role_spec.get("allowed_transforms", [])
                    if isinstance(item, str)
                ]
                if (
                    role.transform is not None
                    and allowed_role_transforms
                    and role.transform not in allowed_role_transforms
                ):
                    result.add_error(
                        f"Transform {role.transform} is not allowed for role "
                        f"{role.role}."
                    )
                if (
                    role.aggregation is not None
                    and role.aggregation not in allowed_aggregations
                ):
                    result.add_error(
                        f"Unsupported aggregation for {role.role}: {role.aggregation}."
                    )
                allowed_role_aggregations = [
                    str(item)
                    for item in role_spec.get("allowed_aggregations", [])
                    if isinstance(item, str)
                ]
                if (
                    role.aggregation is not None
                    and allowed_role_aggregations
                    and role.aggregation not in allowed_role_aggregations
                ):
                    result.add_error(
                        f"Aggregation {role.aggregation} is not allowed for "
                        f"role {role.role}."
                    )

            for item in plan.filters:
                if not isinstance(item, dict):
                    result.add_error("chart filters must be objects.")
                    continue
                operator = item.get("operator")
                if operator is not None and operator not in allowed_filter_operators:
                    result.add_error(f"Unsupported filter operator: {operator}.")
        else:
            if not plan.diagram_nodes:
                result.add_error(f"{visual_type} plans must include diagram_nodes.")
            if not plan.diagram_edges:
                result.add_error(f"{visual_type} plans must include diagram_edges.")

    def _validate_chart(
        self,
        plan: VisualPlan,
        dataset_profile: DatasetProfile | None,
        result: ValidationResult,
    ) -> None:
        x_role = (
            get_role(plan, "x")
            or get_role(plan, "category")
            or get_role(plan, "time_or_order")
        )
        y_role = get_role(plan, "y") or get_role(plan, "measure")

        if x_role is None and plan.chart_type not in {
            "histogram",
            "box_plot",
            "heatmap",
        }:
            result.add_error("chart plans need an x, category, or time_or_order role.")
        if y_role is None and plan.chart_type not in {
            "histogram",
            "box_plot",
            "heatmap",
        }:
            result.add_error("chart plans need a y or measure role.")

        available_fields = (
            {column.name: column.semantic_type for column in dataset_profile.columns}
            if dataset_profile
            else {}
        )

        def field_is_numeric(field: str | None) -> bool:
            return bool(field and available_fields.get(field) == "numeric")

        def field_is_datetime(field: str | None) -> bool:
            return bool(field and available_fields.get(field) == "datetime")

        for role in plan.data_roles:
            if (
                role.field
                and role.field != "row_count"
                and role.field not in available_fields
            ):
                result.add_error(
                    f"{role.role} role field '{role.field}' does not exist "
                    f"in the dataset."
                )

        if (
            plan.chart_type == "line"
            and x_role
            and not (
                field_is_datetime(x_role.field)
                or (x_role.transform in {"week", "month", "day", "year"})
            )
        ):
            result.add_warning("line charts work best with a date or ordered x role.")
        if plan.chart_type == "scatter":
            if not field_is_numeric(x_role.field if x_role else None):
                result.add_error("scatter charts require numeric x.")
            if not field_is_numeric(y_role.field if y_role else None):
                result.add_error("scatter charts require numeric y.")
        if plan.chart_type == "pie":
            if (
                y_role
                and y_role.aggregation != "count"
                and not field_is_numeric(y_role.field)
            ):
                result.add_error("pie charts need a numeric or counted measure.")
            if dataset_profile and len(dataset_profile.columns) > 6:
                result.add_warning("pie charts should avoid too many categories.")
        if plan.chart_type == "histogram":
            value_role = get_role(plan, "value")
            if value_role is None or not field_is_numeric(value_role.field):
                result.add_error("histograms require a numeric value role.")
        if plan.chart_type == "box_plot":
            value_role = get_role(plan, "value")
            if value_role is None or not field_is_numeric(value_role.field):
                result.add_error("box plots require a numeric value role.")
        if plan.chart_type == "heatmap":
            if (
                get_role(plan, "x_category") is None
                or get_role(plan, "y_category") is None
            ):
                result.add_error("heatmaps require x_category and y_category roles.")
        if plan.chart_type == "stacked_bar":
            if get_role(plan, "stack") is None:
                result.add_error("stacked_bar charts require a stack role.")
        if y_role and y_role.field == "row_count" and y_role.aggregation != "count":
            result.add_error("row_count must use count aggregation.")

        if plan.style.orientation and plan.style.orientation not in {
            "vertical",
            "horizontal",
        }:
            result.add_error("style.orientation must be vertical or horizontal.")
        if plan.style.orientation == "horizontal" and plan.chart_type == "bar":
            result.add_warning(
                "horizontal orientation should usually use horizontal_bar."
            )
        if plan.chart_type == "horizontal_bar" and plan.style.orientation is None:
            result.add_warning(
                "horizontal_bar charts should declare style.orientation = horizontal."
            )

    def _validate_diagram(
        self,
        plan: VisualPlan,
        result: ValidationResult,
    ) -> None:
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
                result.add_warning(
                    f"diagram node type '{node.node_type}' is not standard."
                )
        for edge in plan.diagram_edges:
            if edge.source not in known_nodes:
                result.add_error(f"diagram edge source '{edge.source}' does not exist.")
            if edge.target not in known_nodes:
                result.add_error(f"diagram edge target '{edge.target}' does not exist.")
            if edge.label and edge.label not in {"Yes", "No"}:
                result.add_warning(
                    f"diagram edge label '{edge.label}' may not be supported "
                    f"by all renderers."
                )
