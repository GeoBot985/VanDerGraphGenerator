"""Chart.js renderer placeholder."""

from __future__ import annotations

from semantic_visual_builder.data.dataset_context import DatasetContext
from semantic_visual_builder.planning.visual_plan_schema import VisualPlan
from semantic_visual_builder.renderers.base_renderer import BaseRenderer
from semantic_visual_builder.renderers.renderer_result import RendererOutput
from semantic_visual_builder.validation.validation_result import ValidationResult


class ChartJsRenderer(BaseRenderer):
    """Future Chart.js adapter placeholder."""

    name = "chartjs"

    def can_render(self, visual_plan: VisualPlan) -> bool:
        return False

    def render(
        self,
        visual_plan: VisualPlan,
        dataset_context: DatasetContext | None = None,
    ) -> RendererOutput:
        raise NotImplementedError("Chart.js rendering is not yet active.")

    def validate_output(self, output: RendererOutput) -> ValidationResult:
        result = ValidationResult()
        result.add_error("Chart.js rendering is not yet active.")
        return result
