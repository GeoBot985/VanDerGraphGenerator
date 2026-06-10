"""Base renderer contract."""

from __future__ import annotations

from abc import ABC, abstractmethod

from semantic_visual_builder.data.dataset_context import DatasetContext
from semantic_visual_builder.planning.visual_plan_schema import VisualPlan
from semantic_visual_builder.renderers.renderer_result import RendererOutput
from semantic_visual_builder.validation.validation_result import ValidationResult


class BaseRenderer(ABC):
    """Adapter contract for deterministic renderers."""

    name: str

    @abstractmethod
    def can_render(self, visual_plan: VisualPlan) -> bool:
        raise NotImplementedError

    @abstractmethod
    def render(
        self,
        visual_plan: VisualPlan,
        dataset_context: DatasetContext | None = None,
    ) -> RendererOutput:
        raise NotImplementedError

    @abstractmethod
    def validate_output(self, output: RendererOutput) -> ValidationResult:
        raise NotImplementedError
