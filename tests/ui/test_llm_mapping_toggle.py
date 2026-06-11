"""LLM mapping toggle tests."""

from semantic_visual_builder.llm.ollama_client import OllamaModel
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


def test_model_picker_syncs_selected_model_into_app_state() -> None:
    state = AppState()
    state.model_registry.set_models(
        [
            OllamaModel(name="gemma4:12b-it-qat"),
            OllamaModel(name="granite4:3b"),
        ]
    )
    app = SemanticVisualBuilderApp(state, build_ui=False)
    app._model_var = FakeVar("granite4:3b")

    app._sync_selected_model_from_ui()

    assert state.model_registry.selected_model == "granite4:3b"
