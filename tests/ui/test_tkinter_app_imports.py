"""Tkinter app smoke tests."""

from pathlib import Path

from semantic_visual_builder.state.app_state import AppState
from semantic_visual_builder.ui.tkinter_app import SemanticVisualBuilderApp


def test_app_can_be_constructed_without_ui() -> None:
    app = SemanticVisualBuilderApp(AppState(), build_ui=False)
    assert app.app_state.status_messages == []


def test_tkinter_app_does_not_import_message_classifier_or_message_intent() -> None:
    source = Path("src/semantic_visual_builder/ui/tkinter_app.py").read_text()
    assert "MessageClassifier" not in source
    assert "MessageIntent" not in source
