"""Architecture checks to keep the graph matrix contract aligned."""

from __future__ import annotations

import json
from pathlib import Path

from semantic_visual_builder.gallery.gallery_schema import GalleryItem
from semantic_visual_builder.knowledge.graph_matrix import GraphMatrixLoader
from semantic_visual_builder.knowledge.product_kb import ProductKnowledgeLoader
from semantic_visual_builder.renderers.chartjs_renderer import ChartJsRenderer
from semantic_visual_builder.renderers.mermaid_renderer import MermaidRenderer
from semantic_visual_builder.renderers.plotly_renderer import PlotlyRenderer
from semantic_visual_builder.renderers.python_renderer_future import (
    PythonRendererFuture,
)
from semantic_visual_builder.renderers.renderer_registry import RendererRegistry
from semantic_visual_builder.utils.paths import get_graph_matrix_dir, get_kb_dir


def _graph_matrix():
    return GraphMatrixLoader(get_graph_matrix_dir() / "graph_matrix.json").load()


def _renderer_registry() -> RendererRegistry:
    return RendererRegistry(
        [
            PlotlyRenderer(),
            MermaidRenderer(),
            ChartJsRenderer(),
            PythonRendererFuture(),
        ]
    )


def test_gallery_expected_visuals_exist_in_graph_matrix() -> None:
    graph_matrix = _graph_matrix()
    gallery_path = Path("assets/gallery/gallery_items.json")
    data = json.loads(gallery_path.read_text(encoding="utf-8"))
    items = data["items"] if isinstance(data, dict) else data
    gallery_items = [
        GalleryItem.from_dict(item) for item in items if isinstance(item, dict)
    ]

    chart_types = set(graph_matrix.supported_chart_types())
    diagram_types = set(graph_matrix.supported_diagram_types())

    for item in gallery_items:
        if item.expected_chart_type:
            assert item.expected_chart_type in chart_types
        if item.expected_diagram_type:
            assert item.expected_diagram_type in diagram_types


def test_kb_supported_mvp_visuals_exist_in_graph_matrix() -> None:
    graph_matrix = _graph_matrix()
    kb = ProductKnowledgeLoader(get_kb_dir()).load()

    chart_types = set(graph_matrix.supported_chart_types())
    diagram_types = set(graph_matrix.supported_diagram_types())

    for item in kb.chart_types.get("supported_mvp", []):
        if isinstance(item, dict) and item.get("name"):
            assert str(item["name"]) in chart_types
    for item in kb.diagram_types.get("supported_mvp", []):
        if isinstance(item, dict) and item.get("name"):
            assert str(item["name"]) in diagram_types


def test_graph_matrix_renderers_are_supported_by_registry() -> None:
    graph_matrix = _graph_matrix()
    registry = _renderer_registry()
    registry_renderers = set(registry.list_available_renderers())

    for spec in graph_matrix.chart_types().values():
        allowed_renderers = spec.get("allowed_renderers", [])
        if isinstance(allowed_renderers, list):
            for renderer in allowed_renderers:
                assert renderer in registry_renderers
    for spec in graph_matrix.diagram_types().values():
        allowed_renderers = spec.get("allowed_renderers", [])
        if isinstance(allowed_renderers, list):
            for renderer in allowed_renderers:
                assert renderer in registry_renderers


def test_required_roles_exist_in_graph_matrix_roles() -> None:
    graph_matrix = _graph_matrix()
    roles = set(graph_matrix.roles().keys())

    for visual_type in graph_matrix.supported_chart_types():
        for required_role in graph_matrix.required_roles_for(visual_type):
            assert required_role in roles
    for visual_type in graph_matrix.supported_diagram_types():
        for required_role in graph_matrix.required_roles_for(visual_type):
            assert required_role in roles
