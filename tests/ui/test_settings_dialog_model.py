"""Tests for SettingsDialogController."""

from __future__ import annotations

from pathlib import Path

import pytest

from semantic_visual_builder.settings.settings_schema import AppSettings
from semantic_visual_builder.settings.settings_store import SettingsStore
from semantic_visual_builder.ui.settings_dialog import SettingsDialogController


@pytest.fixture()
def controller(tmp_path: Path) -> SettingsDialogController:
    store = SettingsStore(tmp_path / "settings.json")
    return SettingsDialogController(store=store)


class TestSettingsDialogController:
    def test_load_returns_defaults_if_no_file(self, controller: SettingsDialogController) -> None:
        s = controller.load()
        assert s.default_renderer == "plotly"

    def test_current_settings_after_load(self, controller: SettingsDialogController) -> None:
        controller.load()
        s = controller.current_settings()
        assert isinstance(s, AppSettings)

    def test_update_valid_field(self, controller: SettingsDialogController) -> None:
        controller.load()
        errors = controller.update_field("default_renderer", "mermaid")
        assert errors == []
        assert controller.current_settings().default_renderer == "mermaid"

    def test_update_invalid_renderer(self, controller: SettingsDialogController) -> None:
        controller.load()
        errors = controller.update_field("default_renderer", "excel")
        assert len(errors) == 1

    def test_save_returns_success(self, controller: SettingsDialogController) -> None:
        controller.load()
        success, msg = controller.save()
        assert success is True
        assert "saved" in msg.lower()

    def test_save_invalid_settings_returns_error(self, controller: SettingsDialogController) -> None:
        controller.load()
        controller._settings.default_renderer = "invalid_renderer"
        success, msg = controller.save()
        assert success is False

    def test_reset_to_defaults(self, controller: SettingsDialogController) -> None:
        controller.load()
        controller.update_field("debug_mode", True)
        controller.reset_to_defaults()
        assert controller.current_settings().debug_mode is False

    def test_summary_text_contains_renderer(self, controller: SettingsDialogController) -> None:
        controller.load()
        text = controller.summary_text()
        assert "plotly" in text.lower() or "Renderer" in text
