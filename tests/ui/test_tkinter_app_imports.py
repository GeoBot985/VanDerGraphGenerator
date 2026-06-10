"""Tkinter app smoke tests."""

from semantic_visual_builder.state.app_state import AppState
from semantic_visual_builder.ui.tkinter_app import SemanticVisualBuilderApp


def test_app_can_be_constructed_without_ui() -> None:
    app = SemanticVisualBuilderApp(AppState(), build_ui=False)
    assert app.app_state.status_messages == []
