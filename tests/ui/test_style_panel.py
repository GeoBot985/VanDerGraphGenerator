"""Style panel tests."""

from semantic_visual_builder.state.app_state import AppState
from semantic_visual_builder.styles.built_in_styles import list_builtin_style_profiles
from semantic_visual_builder.styles.style_applier import StyleApplicationResult
from semantic_visual_builder.ui.style_panel import StylePanel


def test_style_panel_reflects_active_and_available_styles() -> None:
    state = AppState()
    panel = StylePanel()

    assert "Active style: none" in panel.active_style_text(state)
    assert "Available styles: none" in panel.available_styles_text(state)

    styles = list_builtin_style_profiles()
    state.set_available_style_profiles(styles[:2])
    state.set_active_style_profile(styles[0])
    state.style_application_result = StyleApplicationResult(success=True)

    assert styles[0].style_name in panel.active_style_text(state)
    assert "Application status: success" in panel.active_style_text(state)
    assert styles[0].style_name in panel.summary_text(state)
    assert styles[1].style_name in panel.available_styles_text(state)
