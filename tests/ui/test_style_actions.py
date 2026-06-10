"""Style action tests."""

from pathlib import Path

from semantic_visual_builder.planning.visual_plan_schema import VisualPlan
from semantic_visual_builder.state.app_state import AppState
from semantic_visual_builder.styles.built_in_styles import list_builtin_style_profiles
from semantic_visual_builder.styles.style_manager import StyleManager
from semantic_visual_builder.styles.style_store import StyleStore
from semantic_visual_builder.styles.style_validator import StyleValidator
from semantic_visual_builder.ui.tkinter_app import SemanticVisualBuilderApp


class FakeVar:
    def __init__(self, value: str = "") -> None:
        self.value = value

    def get(self) -> str:
        return self.value

    def set(self, value: str) -> None:
        self.value = value


def _plan() -> VisualPlan:
    plan = VisualPlan(visual_kind="chart", intent="compare")
    plan.style.title = "Total Amount"
    return plan


def test_apply_style_action_uses_selected_profile() -> None:
    state = AppState()
    state.current_visual_plan = _plan()
    styles = list_builtin_style_profiles()
    state.set_available_style_profiles(styles)
    app = SemanticVisualBuilderApp(state, build_ui=False)
    app._style_var = FakeVar(styles[0].style_name)

    message = app.apply_style_action()

    assert "Style applied:" in message
    assert state.current_visual_plan is not None
    assert state.current_visual_plan.metadata.style_profile_id == styles[0].style_id
    assert state.style_application_result is not None


def test_save_load_and_clear_style_actions(monkeypatch, tmp_path: Path) -> None:
    state = AppState()
    state.current_visual_plan = _plan()
    app = SemanticVisualBuilderApp(state, build_ui=False)
    app._style_var = FakeVar()
    app.style_store = StyleStore(tmp_path / "user", tmp_path / "builtin")
    app.style_validator = StyleValidator()
    app.style_manager = StyleManager(app.style_store, app.style_validator)
    app._refresh_available_styles = lambda: None

    monkeypatch.setattr(
        "semantic_visual_builder.ui.tkinter_app.simpledialog.askstring",
        lambda *args, **kwargs: "Custom Style",
    )

    save_message = app.save_style_action()

    assert "Style saved:" in save_message
    saved_files = list((tmp_path / "user").glob("*.style.json"))
    assert saved_files

    monkeypatch.setattr(
        "semantic_visual_builder.ui.tkinter_app.filedialog.askopenfilename",
        lambda **kwargs: str(saved_files[0]),
    )

    load_message = app.load_style_action()

    assert "Style loaded:" in load_message
    assert state.active_style_profile is not None
    assert state.active_style_profile.style_name == "Custom Style"

    clear_message = app.clear_style_action()

    assert clear_message == "Style cleared."
    assert state.active_style_profile is None
