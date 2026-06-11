"""Build prompts for LLM visual intent mapping."""

from __future__ import annotations

import json
from typing import Any

from semantic_visual_builder.data.data_profiler import DatasetProfile
from semantic_visual_builder.knowledge.graph_matrix import GraphMatrix
from semantic_visual_builder.knowledge.product_kb import ProductKnowledgeBase
from semantic_visual_builder.planning.visual_plan import (
    summarize_visual_plan,
    visual_plan_to_dict,
)
from semantic_visual_builder.planning.visual_plan_schema import VisualPlan


class VisualIntentPromptBuilder:
    """Build a grounded prompt for semantic visual mapping."""

    def build_prompt(
        self,
        user_message: str,
        dataset_profile: DatasetProfile | None,
        product_kb: ProductKnowledgeBase | None,
        graph_matrix: GraphMatrix | None,
        current_plan_summary: str | None = None,
        current_plan: VisualPlan | None = None,
    ) -> str:
        lines = [
            "User request:",
            user_message,
            "",
            "Dataset profile:",
        ]
        if dataset_profile is None:
            lines.append("No dataset loaded.")
        else:
            lines.append(f"Rows: {dataset_profile.row_count}")
            for column in dataset_profile.columns:
                samples = ", ".join(column.sample_values[:2])
                column_line = (
                    f"- {column.name}: semantic_type={column.semantic_type}, "
                    f"null_percent={column.null_percent:.2f}, samples=[{samples}]"
                )
                lines.append(column_line)

        contract = self._build_graph_matrix_contract(graph_matrix)
        contract_note = (
            "Use only chart_types, diagram_types, roles, renderers, "
            "aggregations, transforms, and filter operators defined below."
        )
        lines.extend(
            [
                "",
                "Graph matrix authoritative contract:",
                contract_note,
                "Do not invent unsupported visuals or renderers.",
                "Every role object must include a field. For category/measure charts,"
                " use actual dataset columns. If the user asks for a count, use"
                " row_count or a counted measure.",
            ]
        )
        if contract is not None:
            lines.extend(
                [
                    "",
                    "Graph matrix contract:",
                    json.dumps(contract, ensure_ascii=False, separators=(",", ":")),
                ]
            )

        if current_plan_summary:
            lines.extend(["", "Current visual plan summary:", current_plan_summary])
        if current_plan is not None:
            lines.extend(
                [
                    "",
                    "Current visual plan JSON:",
                    json.dumps(visual_plan_to_dict(current_plan), ensure_ascii=False),
                ]
            )

        lines.extend(
            [
                "",
                "Required JSON output contract:",
                (
                    '{"action":"create_plan","visual_kind":"chart",'
                    '"intent":"compare_categories","chart_type":"bar",'
                    '"diagram_type":null,"roles":{'
                    '"category":{"field":"Region"},'
                    '"measure":{"field":"Amount","aggregation":"sum"}},'
                    '"filters":[],"grouping":[],'
                    '"style":{"title":null,"subtitle":null,'
                    '"colour_scheme":null,"highlights":{},'
                    '"labels":{},"orientation":null},"renderer":"plotly",'
                    '"confidence":0.0,"assumptions":[],"questions":[],'
                    '"diagram_nodes":[],"diagram_edges":[]}'
                ),
                (
                    "Action must be one of: create_plan, refine_plan, "
                    "answer_capability, workflow_help, clarification_needed, "
                    "unsupported."
                ),
                "",
                "Return JSON only. Do not include code fences or commentary.",
            ]
        )
        return "\n".join(lines)

    def build_refinement_prompt(
        self,
        user_message: str,
        dataset_profile: DatasetProfile | None,
        product_kb: ProductKnowledgeBase | None,
        graph_matrix: GraphMatrix | None,
        current_plan: VisualPlan,
    ) -> str:
        current_plan_summary = summarize_visual_plan(current_plan)
        lines = [
            "You are updating an existing visual plan.",
            "",
            "Return a complete updated visual-plan JSON object.",
            "Do not return a patch.",
            "Do not generate Python.",
            "Do not generate JavaScript.",
            "Do not generate Mermaid.",
            "Do not change unrelated fields unless the user asked for it.",
            "Preserve existing field mappings unless the user explicitly changes them.",
            "Return JSON only.",
            "",
        ]
        lines.append(
            self.build_prompt(
                user_message=user_message,
                dataset_profile=dataset_profile,
                product_kb=product_kb,
                graph_matrix=graph_matrix,
                current_plan_summary=current_plan_summary,
                current_plan=current_plan,
            )
        )
        return "\n".join(lines)

    def _build_graph_matrix_contract(
        self, graph_matrix: GraphMatrix | None
    ) -> dict[str, Any] | None:
        if graph_matrix is None:
            return None

        def _spec_summary(spec: dict[str, Any]) -> dict[str, Any]:
            summary: dict[str, Any] = {}
            for key in (
                "visual_kind",
                "intent",
                "required_roles",
                "optional_roles",
                "allowed_renderers",
            ):
                value = spec.get(key)
                if value is not None:
                    summary[key] = value
            return summary

        def _role_summary(spec: dict[str, Any]) -> dict[str, Any]:
            summary: dict[str, Any] = {}
            for key in (
                "semantic_types",
                "allowed_visual_kinds",
                "allowed_chart_types",
                "allowed_diagram_types",
                "allowed_aggregations",
                "allowed_transforms",
            ):
                value = spec.get(key)
                if value is not None:
                    summary[key] = value
            return summary

        return {
            "schema_version": graph_matrix.schema_version(),
            "visual_kinds": graph_matrix.visual_kinds(),
            "actions": graph_matrix.raw.get("actions", []),
            "allowed_aggregations": graph_matrix.allowed_aggregations(),
            "allowed_transforms": graph_matrix.allowed_transforms(),
            "allowed_filter_operators": graph_matrix.allowed_filter_operators(),
            "roles": {
                name: _role_summary(spec)
                for name, spec in graph_matrix.roles().items()
                if isinstance(spec, dict)
            },
            "chart_types": {
                name: _spec_summary(spec)
                for name, spec in graph_matrix.chart_types().items()
                if isinstance(spec, dict)
            },
            "diagram_types": {
                name: _spec_summary(spec)
                for name, spec in graph_matrix.diagram_types().items()
                if isinstance(spec, dict)
            },
        }
