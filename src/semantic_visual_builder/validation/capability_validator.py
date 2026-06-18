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

        self._validate_three_d(plan, result)
        return result

    def _validate_three_d(self, plan: VisualPlan, result: ValidationResult) -> None:
        """Sanity-check the chart_style / depth knobs are within MVP support."""
        style = getattr(plan.style, "chart_style", None)
        if style is None:
            return
        allowed_styles = {"flat", "soft_3d", "true_3d"}
        if style not in allowed_styles:
            result.add_error(
                f"Chart style '{style}' is not supported in the MVP. "
                "Expected one of: flat, soft_3d, true_3d."
            )
            return
        if style == "true_3d":
            renderer = plan.render_target.renderer
            if renderer not in {"plotly", None}:
                result.add_error(
                    f"True 3D scenes are only available with the Plotly renderer, "
                    f"not '{renderer}'."
                )
        if style in {"soft_3d", "true_3d"} and plan.visual_kind == "diagram":
            renderer = plan.render_target.renderer
            if renderer not in {"mermaid", None}:
                result.add_warning(
                    f"Soft 3D / true 3D for diagrams only layers shadows and shapes "
                    f"in Mermaid; requested renderer '{renderer}' may ignore it."
                )

        depth = getattr(plan.style, "depth", None)
        if depth is not None and depth < 0:
            result.add_error("style.depth must be >= 0.")
        perspective = getattr(plan.style, "perspective", None)
        if perspective is not None and not 0.0 <= perspective <= 1.0:
            result.add_error("style.perspective must be between 0.0 and 1.0.")
        lighting = getattr(plan.style, "lighting", None)
        if lighting is not None and lighting not in {"flat", "soft", "dramatic"}:
            result.add_error(
                f"Unsupported lighting: {lighting!r}. Expected flat, soft, dramatic."
            )
        tilt = getattr(plan.style, "tilt", None)
        if tilt is not None and not -180 <= tilt <= 180:
            result.add_error("style.tilt must be between -180 and 180.")
