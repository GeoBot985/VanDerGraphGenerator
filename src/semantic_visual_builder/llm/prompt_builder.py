"""Build prompts for LLM visual intent mapping."""

from __future__ import annotations

from semantic_visual_builder.data.data_profiler import DatasetProfile
from semantic_visual_builder.knowledge.graph_matrix import GraphMatrix
from semantic_visual_builder.knowledge.product_kb import ProductKnowledgeBase


class VisualIntentPromptBuilder:
    """Build a grounded prompt for semantic visual mapping."""

    def build_prompt(
        self,
        user_message: str,
        dataset_profile: DatasetProfile | None,
        product_kb: ProductKnowledgeBase | None,
        graph_matrix: GraphMatrix | None,
        current_plan_summary: str | None = None,
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

        lines.extend(
            [
                "",
                "Required JSON output contract:",
                '{"visual_kind":"chart","intent":"compare_categories","chart_type":"bar","diagram_type":null,"roles":{},"filters":[],"grouping":[],"style":{"title":null,"colour_scheme":null,"highlights":{}},"renderer":"plotly","confidence":0.0,"assumptions":[],"questions":[]}',
                "",
                "Return JSON only. Do not include code fences or commentary.",
            ]
        )
        return "\n".join(lines)
