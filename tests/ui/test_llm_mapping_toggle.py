"""LLM mapping toggle tests."""

from semantic_visual_builder.state.app_state import AppState
from semantic_visual_builder.ui.tkinter_app import SemanticVisualBuilderApp


class FakeVar:
    def __init__(self, value):
        self.value = value

    def get(self):
        return self.value

    def set(self, value):
        self.value = value


def test_toggle_state_can_be_updated() -> None:
    state = AppState()
    app = SemanticVisualBuilderApp(state, build_ui=False)
    app._use_llm_var = FakeVar(False)
    app._on_toggle_llm_mapping()
    assert state.llm_mapping_enabled is False


def test_disabled_toggle_routes_to_deterministic_mapping() -> None:
    state = AppState()
    state.set_llm_mapping_enabled(False)
    assert state.llm_mapping_enabled is False
