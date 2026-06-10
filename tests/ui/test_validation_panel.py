"""Validation panel tests."""

from semantic_visual_builder.state.app_state import AppState
from semantic_visual_builder.ui.validation_panel import ValidationPanel
from semantic_visual_builder.validation.validation_result import ValidationResult


def test_validation_panel_groups_errors_warnings_info() -> None:
    state = AppState()
    state.current_validation_result = ValidationResult()
    state.current_validation_result.add_error("Broken")
    state.current_validation_result.add_warning("Careful")
    state.current_validation_result.add_info("Good")
    panel = ValidationPanel()
    text = panel.validation_text(state)
    assert "Errors:" in text
    assert "- Broken" in text
    assert "Warnings:" in text
    assert "Info:" in text


def test_validation_panel_reports_plan_status() -> None:
    state = AppState()
    panel = ValidationPanel()
    assert panel.plan_status_text(state) == "No plan"
