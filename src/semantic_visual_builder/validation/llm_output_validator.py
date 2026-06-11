"""Validate LLM draft JSON before conversion to a visual plan."""

from __future__ import annotations

from typing import Any

from semantic_visual_builder.knowledge.graph_matrix import GraphMatrix

from .validation_result import ValidationResult


class LlmOutputValidator:
    """Validate semantic mapping drafts."""

    def validate_draft_json(
        self,
        data: dict[str, Any],
        graph_matrix: GraphMatrix | None,
    ) -> ValidationResult:
        result = ValidationResult()
        if graph_matrix is None:
            result.add_error("graph_matrix is required for LLM output validation.")
            return result

        required_fields = ("action", "visual_kind", "intent", "roles")
        for field in required_fields:
            if field not in data:
                result.add_error(f"Missing required field: {field}.")

        action = data.get("action")
        if action is not None:
            allowed_actions = [
                str(item)
                for item in graph_matrix.raw.get("actions", [])
                if isinstance(item, str)
            ]
            if allowed_actions and action not in allowed_actions:
                result.add_error(f"Unsupported action: {action}.")

        visual_kind = data.get("visual_kind")
        if visual_kind is not None and visual_kind not in graph_matrix.visual_kinds():
            result.add_error(f"Unsupported visual_kind: {visual_kind}.")

        roles = data.get("roles")
        if roles is not None and not isinstance(roles, dict):
            result.add_error("roles must be an object.")

        chart_type = data.get("chart_type")
        diagram_type = data.get("diagram_type")

        if visual_kind == "chart":
            if chart_type is None:
                result.add_error("chart draft must include chart_type.")
            elif chart_type not in graph_matrix.supported_chart_types():
                result.add_error(f"Unsupported chart_type: {chart_type}.")
            if diagram_type is not None:
                result.add_error("diagram_type only applies to diagram drafts.")
            if chart_type is not None and not graph_matrix.renderer_allowed(
                str(chart_type), data.get("renderer")
            ):
                renderer = data.get("renderer")
                result.add_error(
                    f"Unsupported renderer: {renderer} for chart_type "
                    f"{chart_type}."
                )
            if isinstance(roles, dict) and chart_type is not None:
                self._validate_roles(roles, str(chart_type), graph_matrix, result)

        if visual_kind == "diagram":
            if diagram_type is None:
                result.add_error("diagram draft must include diagram_type.")
            elif diagram_type not in graph_matrix.supported_diagram_types():
                result.add_error(f"Unsupported diagram_type: {diagram_type}.")
            if chart_type is not None:
                result.add_error("chart_type only applies to chart drafts.")
            if diagram_type is not None and not graph_matrix.renderer_allowed(
                str(diagram_type), data.get("renderer")
            ):
                renderer = data.get("renderer")
                result.add_error(
                    f"Unsupported renderer: {renderer} for diagram_type "
                    f"{diagram_type}."
                )
            diagram_nodes = data.get("diagram_nodes", [])
            diagram_edges = data.get("diagram_edges", [])
            if not isinstance(diagram_nodes, list) or not diagram_nodes:
                result.add_error("diagram draft must include diagram_nodes.")
            if not isinstance(diagram_edges, list) or not diagram_edges:
                result.add_error("diagram draft must include diagram_edges.")
            if isinstance(diagram_nodes, list):
                for node in diagram_nodes:
                    if (
                        not isinstance(node, dict)
                        or not node.get("id")
                        or not node.get("label")
                    ):
                        result.add_error(
                            "diagram_nodes entries must include id and label."
                        )
            if isinstance(diagram_edges, list):
                for edge in diagram_edges:
                    if (
                        not isinstance(edge, dict)
                        or not edge.get("source")
                        or not edge.get("target")
                    ):
                        result.add_error(
                            "diagram_edges entries must include source and target."
                        )

        confidence = data.get("confidence")
        if confidence is not None:
            if (
                isinstance(confidence, bool)
                or not isinstance(confidence, (int, float))
                or not 0 <= float(confidence) <= 1
            ):
                result.add_error("confidence must be numeric between 0 and 1.")

        style = data.get("style")
        if style is not None and not isinstance(style, dict):
            result.add_error("style must be an object.")
        if isinstance(style, dict):
            title_size = style.get("title_size")
            if title_size is not None and (
                isinstance(title_size, bool)
                or not isinstance(title_size, (int, float))
                or int(title_size) <= 0
            ):
                result.add_error("style.title_size must be a positive integer.")
            orientation = style.get("orientation")
            if orientation is not None and orientation not in {
                "vertical",
                "horizontal",
            }:
                result.add_error(f"Unsupported orientation: {orientation}.")
            highlights = style.get("highlights")
            if highlights is not None and not isinstance(highlights, dict):
                result.add_error("style.highlights must be an object.")
            labels = style.get("labels")
            if labels is not None and not isinstance(labels, dict):
                result.add_error("style.labels must be an object.")

        if "diagram_nodes" in data and not isinstance(data.get("diagram_nodes"), list):
            result.add_error("diagram_nodes must be a list.")
        if "diagram_edges" in data and not isinstance(data.get("diagram_edges"), list):
            result.add_error("diagram_edges must be a list.")

        if visual_kind == "diagram":
            nodes = data.get("diagram_nodes", [])
            edges = data.get("diagram_edges", [])
            if not isinstance(nodes, list) or not nodes:
                result.add_warning("diagram drafts should include diagram_nodes.")
            if not isinstance(edges, list) or not edges:
                result.add_warning("diagram drafts should include diagram_edges.")
            for node in nodes if isinstance(nodes, list) else []:
                if (
                    not isinstance(node, dict)
                    or not node.get("id")
                    or not node.get("label")
                ):
                    result.add_error("diagram_nodes entries must include id and label.")
            for edge in edges if isinstance(edges, list) else []:
                if (
                    not isinstance(edge, dict)
                    or not edge.get("source")
                    or not edge.get("target")
                ):
                    result.add_error(
                        "diagram_edges entries must include source and target."
                    )

        filters = data.get("filters", [])
        if filters is not None:
            if not isinstance(filters, list):
                result.add_error("filters must be a list.")
            else:
                for item in filters:
                    if not isinstance(item, dict):
                        result.add_error("filters entries must be objects.")
                        continue
                    operator = item.get("operator")
                    if (
                        operator is not None
                        and operator not in graph_matrix.allowed_filter_operators()
                    ):
                        result.add_error(f"Unsupported filter operator: {operator}.")

        return result

    def _validate_roles(
        self,
        roles: dict[str, Any],
        visual_type: str,
        graph_matrix: GraphMatrix,
        result: ValidationResult,
    ) -> None:
        spec = graph_matrix.get_visual_spec(visual_type) or {}
        allowed_roles = graph_matrix.allowed_roles_for(visual_type)
        required_roles = graph_matrix.required_roles_for(visual_type)
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

        for required_role in required_roles:
            if required_role not in roles:
                result.add_error(
                    f"{visual_type} drafts must include role: {required_role}."
                )

        for role_name, role_data in roles.items():
            if allowed_roles and role_name not in allowed_roles:
                result.add_error(f"Unsupported role for {visual_type}: {role_name}.")
                continue
            role_spec = graph_matrix.roles().get(role_name, {})
            if isinstance(role_data, dict):
                aggregation = role_data.get("aggregation")
                transform = role_data.get("transform")
                if aggregation is not None and aggregation not in allowed_aggregations:
                    result.add_error(
                        f"Unsupported aggregation for {role_name}: {aggregation}."
                    )
                if transform is not None and transform not in allowed_transforms:
                    result.add_error(
                        f"Unsupported transform for {role_name}: {transform}."
                    )
                allowed_role_aggregations = [
                    str(item)
                    for item in role_spec.get("allowed_aggregations", [])
                    if isinstance(item, str)
                ]
                if (
                    aggregation is not None
                    and allowed_role_aggregations
                    and aggregation not in allowed_role_aggregations
                ):
                    result.add_error(
                        f"Aggregation {aggregation} is not allowed for role "
                        f"{role_name}."
                    )
                allowed_role_transforms = [
                    str(item)
                    for item in role_spec.get("allowed_transforms", [])
                    if isinstance(item, str)
                ]
                if (
                    transform is not None
                    and allowed_role_transforms
                    and transform not in allowed_role_transforms
                ):
                    result.add_error(
                        f"Transform {transform} is not allowed for role "
                        f"{role_name}."
                    )
