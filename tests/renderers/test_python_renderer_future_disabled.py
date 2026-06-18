"""Python renderer future tests."""

import pytest

from semantic_visual_builder.planning.intent_mapper import IntentMapper
from semantic_visual_builder.renderers.chartjs_renderer import ChartJsRenderer
from semantic_visual_builder.renderers.mermaid_renderer import MermaidRenderer
from semantic_visual_builder.renderers.plotly_renderer import PlotlyRenderer
from semantic_visual_builder.renderers.python_renderer_future import (
    PythonRendererFuture,
)
from semantic_visual_builder.renderers.renderer_registry import RendererRegistry


def test_can_render_always_false() -> None:
    assert PythonRendererFuture().can_render(object()) is False


def test_render_raises() -> None:
    with pytest.raises(NotImplementedError):
        PythonRendererFuture().render(object())


def test_registry_never_selects_it() -> None:
    plan = IntentMapper().map_request_to_plan("Show transactions per week", None)
    renderer = RendererRegistry([PlotlyRenderer(), MermaidRenderer(), ChartJsRenderer(), PythonRendererFuture()]).get_renderer(plan)
    assert not isinstance(renderer, PythonRendererFuture)
