"""Validate that a plan stays within MVP capabilities."""

from __future__ import annotations

from semantic_visual_builder.knowledge.product_kb import ProductKnowledgeBase
from semantic_visual_builder.planning.visual_plan_schema import VisualPlan

from .validation_result import ValidationResult


class CapabilityValidator:
    """Check that plans use supported MVP features."""

    def validate_against_capabilities(
        self,
        plan: VisualPlan,
        product_kb: ProductKnowledgeBase,
    ) -> ValidationResult:
        result = ValidationResult()
        supported_charts = {
            item.get("name", "")
            for item in product_kb.chart_types.get("supported_mvp", [])
            if isinstance(item, dict)
        }
        supported_diagrams = {
            item.get("name", "")
            for item in product_kb.diagram_types.get("supported_mvp", [])
            if isinstance(item, dict)
        }
        if plan.visual_kind == "chart" and plan.chart_type and plan.chart_type not in supported_charts:
            result.add_error(f"Chart type '{plan.chart_type}' is not supported in the MVP.")
        if plan.visual_kind == "diagram" and plan.diagram_type and plan.diagram_type not in supported_diagrams:
            result.add_error(f"Diagram type '{plan.diagram_type}' is not supported in the MVP.")
        if plan.render_target.renderer == "python":
            result.add_error("Generated Python renderer is not supported in the MVP.")
        if plan.render_target.renderer == "graphviz":
            result.add_error("Graphviz is not supported in the MVP.")
        return result
