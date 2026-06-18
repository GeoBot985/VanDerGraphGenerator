"""Architecture guards for desktop UI wiring.

These tests prevent the built-but-unexposed regression pattern: library
modules that exist and are unit-tested but are never instantiated by the
Tkinter app. They also guard the Chart.js silent-trap fix.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from semantic_visual_builder.renderers.chartjs_renderer import ChartJsRenderer
from semantic_visual_builder.renderers.mermaid_renderer import MermaidRenderer
from semantic_visual_builder.renderers.plotly_renderer import PlotlyRenderer
from semantic_visual_builder.renderers.python_renderer_future import (
    PythonRendererFuture,
)
from semantic_visual_builder.renderers.renderer_registry import RendererRegistry
from semantic_visual_builder.state.app_state import AppState
from semantic_visual_builder.ui.tkinter_app import SemanticVisualBuilderApp


def _app_source() -> str:
    return Path("src/semantic_visual_builder/ui/tkinter_app.py").read_text(
        encoding="utf-8"
    )


def _bootstrap_source() -> str:
    return Path("src/semantic_visual_builder/app.py").read_text(encoding="utf-8")


def test_app_instantiates_all_ui_controllers() -> None:
    app = SemanticVisualBuilderApp(AppState(), build_ui=False)
    assert isinstance(app.gallery_panel.items, list)
    assert app.settings_dialog is not None
    assert app.export_dialog is not None
    assert app.style_comparison_panel is not None
    assert app.excel_loader is not None
    assert app.export_manager is not None


def test_app_loads_gallery_items_at_startup() -> None:
    app = SemanticVisualBuilderApp(AppState(), build_ui=False)
    assert len(app.gallery_panel.items) >= 1
    assert app.app_state.gallery_items == app.gallery_panel.items


def test_tkinter_app_wires_excel_and_export_menus() -> None:
    source = _app_source()
    assert "load_excel_action" in source
    assert "export_report_html_action" in source
    assert "export_png_action" in source
    assert "export_svg_action" in source
    assert "open_settings_action" in source
    assert "compare_styles_action" in source
    assert "reload_gallery_items_action" in source


def test_tkinter_app_has_gallery_and_style_comparison_tabs() -> None:
    source = _app_source()
    assert '_add_text_tab("Gallery")' in source
    assert '_add_text_tab("Style Compare")' in source


def test_bootstrap_loads_and_applies_settings() -> None:
    source = _bootstrap_source()
    assert "SettingsManager" in source
    assert "apply_to_app_state" in source
    assert "get_settings_path" in source


def test_chartjs_renderer_is_rejected_at_routing_time() -> None:
    from semantic_visual_builder.planning.intent_mapper import IntentMapper

    plan = IntentMapper().map_request_to_plan("Show transactions per week", None)
    plan.render_target.renderer = "chartjs"
    registry = RendererRegistry(
        [PlotlyRenderer(), MermaidRenderer(), ChartJsRenderer(), PythonRendererFuture()]
    )
    with pytest.raises(ValueError):
        registry.get_renderer(plan)
