"""Renderer registry tests."""

from pathlib import Path

import pytest

from semantic_visual_builder.data.csv_loader import CsvLoader
from semantic_visual_builder.data.data_profiler import DataProfiler
from semantic_visual_builder.planning.field_mapper import FieldMapper
from semantic_visual_builder.planning.intent_mapper import IntentMapper
from semantic_visual_builder.renderers.chartjs_renderer import ChartJsRenderer
from semantic_visual_builder.renderers.mermaid_renderer import MermaidRenderer
from semantic_visual_builder.renderers.plotly_renderer import PlotlyRenderer
from semantic_visual_builder.renderers.python_renderer_future import (
    PythonRendererFuture,
)
from semantic_visual_builder.renderers.renderer_registry import RendererRegistry


def _sample_profile():
    root = Path(__file__).resolve().parents[2]
    dataframe = CsvLoader().load(root / "assets" / "samples" / "sample_transactions.csv").dataframe
    return DataProfiler().profile(dataframe)


def test_chart_plan_defaults_to_plotly_renderer() -> None:
    profile = _sample_profile()
    plan = FieldMapper().propose_roles("Show transactions per week", profile, IntentMapper().map_request_to_plan("Show transactions per week", profile))
    renderer = RendererRegistry([PlotlyRenderer(), MermaidRenderer(), ChartJsRenderer(), PythonRendererFuture()]).get_renderer(plan)
    assert isinstance(renderer, PlotlyRenderer)


def test_diagram_flowchart_defaults_to_mermaid_renderer() -> None:
    plan = IntentMapper().map_request_to_plan("Create a flowchart: A user submits a request.", None)
    renderer = RendererRegistry([PlotlyRenderer(), MermaidRenderer(), ChartJsRenderer(), PythonRendererFuture()]).get_renderer(plan)
    assert isinstance(renderer, MermaidRenderer)


def test_unsupported_renderer_raises_clear_value_error() -> None:
    plan = IntentMapper().map_request_to_plan("Show transactions per week", _sample_profile())
    plan.render_target.renderer = "unsupported"
    registry = RendererRegistry([PlotlyRenderer(), MermaidRenderer(), ChartJsRenderer(), PythonRendererFuture()])
    with pytest.raises(ValueError):
        registry.get_renderer(plan)


def test_python_renderer_future_is_not_selected() -> None:
    plan = IntentMapper().map_request_to_plan("Show transactions per week", _sample_profile())
    renderer = RendererRegistry([PlotlyRenderer(), MermaidRenderer(), ChartJsRenderer(), PythonRendererFuture()]).get_renderer(plan)
    assert not isinstance(renderer, PythonRendererFuture)


def test_list_available_renderers_excludes_python_future() -> None:
    registry = RendererRegistry([PlotlyRenderer(), MermaidRenderer(), ChartJsRenderer(), PythonRendererFuture()])
    assert "plotly" in registry.list_available_renderers()
    assert "mermaid" in registry.list_available_renderers()
    assert "python_future" not in registry.list_available_renderers()
