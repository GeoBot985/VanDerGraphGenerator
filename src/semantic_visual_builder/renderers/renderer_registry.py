"""Renderer registry for selecting deterministic adapters."""

from __future__ import annotations

from semantic_visual_builder.planning.visual_plan_schema import VisualPlan

from .base_renderer import BaseRenderer
from .python_renderer_future import PythonRendererFuture


class RendererRegistry:
    """Select the correct renderer for a plan."""

    def __init__(self, renderers: list[BaseRenderer]):
        self.renderers = renderers

    def get_renderer(self, visual_plan: VisualPlan) -> BaseRenderer:
        desired = visual_plan.render_target.renderer
        if desired in {"python", "python_future"}:
            raise ValueError("PythonRendererFuture is disabled in the MVP.")
        if visual_plan.visual_kind == "chart":
            if desired == "chartjs":
                raise ValueError(
                    "Chart.js rendering is not yet active. "
                    "Use the Plotly renderer instead."
                )
            if desired not in {None, "", "plotly"}:
                raise ValueError(f"Unsupported chart renderer '{desired}'.")
            return self._find_renderer("plotly")
        if visual_plan.visual_kind == "diagram":
            if visual_plan.diagram_type == "flowchart" or desired in {None, "", "mermaid"}:
                return self._find_renderer("mermaid")
            raise ValueError(f"Unsupported diagram renderer '{desired}'.")
        raise ValueError(f"No renderer can handle visual kind '{visual_plan.visual_kind}' and renderer '{desired}'.")

    def list_available_renderers(self) -> list[str]:
        names = [renderer.name for renderer in self.renderers if not isinstance(renderer, PythonRendererFuture)]
        return names

    def _find_renderer(self, name: str) -> BaseRenderer:
        for renderer in self.renderers:
            if isinstance(renderer, PythonRendererFuture):
                continue
            if renderer.name == name:
                return renderer
        raise ValueError(f"No renderer registered for '{name}'.")
