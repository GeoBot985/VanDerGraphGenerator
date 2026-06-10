"""Future Python renderer plugin placeholder.

Future plugin only. Not active in MVP. Do not execute generated Python in MVP.
"""

from .base_renderer import BaseRenderer
from semantic_visual_builder.data.dataset_context import DatasetContext
from semantic_visual_builder.planning.visual_plan_schema import VisualPlan
from semantic_visual_builder.renderers.renderer_result import RendererOutput
from semantic_visual_builder.validation.validation_result import ValidationResult


class PythonRendererFuture(BaseRenderer):
    """Disabled future plugin stub."""

    name = "python_future"

    def can_render(self, visual_plan: VisualPlan) -> bool:
        return False

    def render(
        self,
        visual_plan: VisualPlan,
        dataset_context: DatasetContext | None = None,
    ) -> RendererOutput:
        raise NotImplementedError("Generated Python rendering is not active in the MVP.")

    def validate_output(self, output: RendererOutput) -> ValidationResult:
        result = ValidationResult()
        result.add_error("Generated Python rendering is not active in the MVP.")
        return result
