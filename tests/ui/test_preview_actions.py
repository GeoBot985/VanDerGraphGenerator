"""Preview action tests."""

from pathlib import Path

from semantic_visual_builder.data.csv_loader import CsvLoader
from semantic_visual_builder.data.data_profiler import DataProfiler
from semantic_visual_builder.planning.field_mapper import FieldMapper
from semantic_visual_builder.planning.intent_mapper import IntentMapper
from semantic_visual_builder.state.app_state import AppState
from semantic_visual_builder.ui.tkinter_app import SemanticVisualBuilderApp
from semantic_visual_builder.validation.validation_result import ValidationResult


def test_generate_preview_creates_html_and_tracks_output(monkeypatch, tmp_path) -> None:
    root = Path(__file__).resolve().parents[2]
    loaded = CsvLoader().load(root / "assets" / "samples" / "sample_transactions.csv")
    profile = DataProfiler().profile(loaded.dataframe)
    plan = FieldMapper().propose_roles("Show transactions per week", profile, IntentMapper().map_request_to_plan("Show transactions per week", profile))
    state = AppState()
    state.dataset_context.loaded_dataset = loaded
    state.dataset_context.profile = profile
    state.current_visual_plan = plan
    state.current_validation_result = ValidationResult()
    app = SemanticVisualBuilderApp(state, build_ui=False)
    app.html_exporter.export_dir = tmp_path / "previews"
    monkeypatch.setattr(app.preview_host, "open_preview", lambda path: None)

    message = app.generate_preview()

    assert "Preview generated:" in message
    assert state.last_renderer_output is not None
    assert state.last_preview_path is not None
    assert state.last_preview_path.exists()


def test_open_last_preview_handles_missing_preview() -> None:
    app = SemanticVisualBuilderApp(AppState(), build_ui=False)
    assert "No preview file" in app.open_last_preview()


def test_open_last_preview_uses_existing_preview(monkeypatch, tmp_path) -> None:
    state = AppState()
    state.last_preview_path = tmp_path / "preview.html"
    state.last_preview_path.write_text("<html></html>", encoding="utf-8")
    app = SemanticVisualBuilderApp(state, build_ui=False)
    calls = []
    monkeypatch.setattr(app.preview_host, "open_preview", lambda path: calls.append(path))
    message = app.open_last_preview()
    assert "Opened preview:" in message
    assert calls and calls[0] == state.last_preview_path
