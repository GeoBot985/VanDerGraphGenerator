"""Build prompts for LLM visual intent mapping."""

from __future__ import annotations

import json

from semantic_visual_builder.data.data_profiler import DatasetProfile
from semantic_visual_builder.knowledge.graph_matrix import GraphMatrix
from semantic_visual_builder.knowledge.product_kb import ProductKnowledgeBase
from semantic_visual_builder.planning.visual_plan import summarize_visual_plan, visual_plan_to_dict
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
                lines.append(
                    f"- {column.name}: semantic_type={column.semantic_type}, null_percent={column.null_percent:.2f}, samples=[{samples}]"
                )

        lines.extend(["", "Supported chart types:"])
        if product_kb is not None:
            for item in product_kb.chart_types.get("supported_mvp", []):
                if isinstance(item, dict):
                    lines.append(f"- {item.get('name')}: {item.get('purpose')}")

            lines.extend(["", "Supported diagram types:"])
            for item in product_kb.diagram_types.get("supported_mvp", []):
                if isinstance(item, dict):
                    lines.append(f"- {item.get('name')}: {item.get('purpose')}")

            lines.extend(["", "Supported renderers:"])
            lines.append("- plotly")
            lines.append("- chartjs")
            lines.append("- mermaid")
            lines.extend(["", "MVP limitations:"])
            for item in product_kb.limitations.get("mvp_limitations", []):
                lines.append(f"- {item}")

        if graph_matrix is not None:
            lines.extend(["", "Supported intents:"])
            for intent in graph_matrix.list_intents():
                lines.append(f"- {intent}")

        if current_plan_summary:
            lines.extend(["", "Current visual plan summary:", current_plan_summary])
        if current_plan is not None:
            lines.extend(["", "Current visual plan JSON:", json.dumps(visual_plan_to_dict(current_plan), ensure_ascii=False)])

        lines.extend(
            [
                "",
                "Required JSON output contract:",
                '{"visual_kind":"chart","intent":"compare_categories","chart_type":"bar","diagram_type":null,"roles":{},"filters":[],"grouping":[],"style":{"title":null,"subtitle":null,"colour_scheme":null,"highlights":{},"labels":{},"orientation":null},"renderer":"plotly","confidence":0.0,"assumptions":[],"questions":[],"diagram_nodes":[],"diagram_edges":[]}',
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
        lines.append(self.build_prompt(
            user_message=user_message,
            dataset_profile=dataset_profile,
            product_kb=product_kb,
            graph_matrix=graph_matrix,
            current_plan_summary=current_plan_summary,
            current_plan=current_plan,
        ))
        return "\n".join(lines)
