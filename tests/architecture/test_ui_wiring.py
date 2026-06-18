"""Architecture guards for desktop UI wiring.

These tests prevent the built-but-unexposed regression pattern: library
modules that exist and are unit-tested but are never instantiated by the
Tkinter app. They also guard the Chart.js silent-trap fix.
"""

from __future__ import annotations

import pathlib
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


def test_ollama_client_chat_is_implemented() -> None:
    from semantic_visual_builder.llm.ollama_client import OllamaClient

    source = Path("src/semantic_visual_builder/llm/ollama_client.py").read_text(
        encoding="utf-8"
    )
    assert "NotImplementedError" not in source.split("def chat(")[1].split("def ")[0]
    # chat() must validate inputs rather than raising NotImplementedError.
    client = OllamaClient()
    import pytest

    with pytest.raises(ValueError):
        client.chat(model="m", messages=[])


def test_refinement_orchestrator_supports_chat_history_routing() -> None:
    source = Path("src/semantic_visual_builder/planning/refinement_orchestrator.py").read_text(
        encoding="utf-8"
    )
    assert "map_to_draft_with_history" in source
    assert "_conversation_history" in source


def test_llm_semantic_mapper_exposes_chat_history_mapping() -> None:
    source = Path("src/semantic_visual_builder/llm/llm_semantic_mapper.py").read_text(
        encoding="utf-8"
    )
    assert "def map_to_draft_with_history" in source
    assert "self.ollama_client.chat(" in source


def test_png_and_svg_exporters_use_playwright() -> None:
    for module_name in ("png_exporter.py", "svg_exporter.py"):
        source = pathlib.Path("src/semantic_visual_builder/export") / module_name
        assert "PlaywrightExporter" in source.read_text(encoding="utf-8")


def test_app_settings_schema_carries_ollama_base_url_and_timeout() -> None:
    from semantic_visual_builder.settings.settings_schema import AppSettings

    settings = AppSettings()
    assert settings.ollama_base_url == "http://localhost:11434"
    assert settings.generation_timeout_seconds > 0
    assert "ollama_base_url" in settings.to_dict()
    assert "generation_timeout_seconds" in settings.to_dict()
    rebuilt = AppSettings.from_dict(settings.to_dict())
    assert rebuilt.ollama_base_url == settings.ollama_base_url


def test_settings_dialog_rejects_chartjs_renderer() -> None:
    from semantic_visual_builder.settings.settings_store import SettingsStore
    from semantic_visual_builder.ui.settings_dialog import SettingsDialogController

    controller = SettingsDialogController(store=SettingsStore(pathlib.Path("/tmp/_unused.json")))
    controller.load()
    errors = controller.update_field("default_renderer", "chartjs")
    assert errors, "chartjs must not be offered as a renderer option"


def test_tkinter_app_uses_open_in_os_not_os_startfile() -> None:
    source = Path("src/semantic_visual_builder/ui/tkinter_app.py").read_text(encoding="utf-8")
    assert "os.startfile" not in source
    assert "open_in_os" in source


def test_tkinter_app_exposes_style_review_action() -> None:
    source = Path("src/semantic_visual_builder/ui/tkinter_app.py").read_text(encoding="utf-8")
    assert "def review_extracted_style_action" in source
    assert "StyleReviewDialogController" in source
    assert "editable_draft_from_style_profile" in source


def test_app_supports_headless_flags() -> None:
    from semantic_visual_builder.app import parse_args

    args = parse_args(["--no-llm", "--dataset", "sample.csv"])
    assert args.no_llm is True
    assert args.dataset == "sample.csv"

