"""Renderer contract stub tests."""

from semantic_visual_builder.renderers.chartjs_renderer import ChartJsRenderer
from semantic_visual_builder.renderers.mermaid_renderer import MermaidRenderer
from semantic_visual_builder.renderers.plotly_renderer import PlotlyRenderer
from semantic_visual_builder.renderers.python_renderer_future import (
    PythonRendererFuture,
)


def test_renderer_classes_exist() -> None:
    assert MermaidRenderer is not None
    assert PlotlyRenderer is not None
    assert ChartJsRenderer is not None
    assert PythonRendererFuture is not None
