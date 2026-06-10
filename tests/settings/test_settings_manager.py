"""Tests for SettingsManager."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

import pytest

from semantic_visual_builder.settings.settings_manager import SettingsManager
from semantic_visual_builder.settings.settings_schema import AppSettings
from semantic_visual_builder.settings.settings_store import SettingsStore


@pytest.fixture()
def manager(tmp_path: Path) -> SettingsManager:
    store = SettingsStore(tmp_path / "settings.json")
    return SettingsManager(store)


class TestSettingsManager:
    def test_load_returns_settings(self, manager: SettingsManager) -> None:
        s = manager.load_settings()
        assert isinstance(s, AppSettings)

    def test_save_and_load_roundtrip(self, manager: SettingsManager) -> None:
        s = AppSettings(default_renderer="mermaid")
        manager.save_settings(s)
        loaded = manager.load_settings()
        assert loaded.default_renderer == "mermaid"

    def test_apply_to_app_state_sets_llm_flag(self, manager: SettingsManager) -> None:
        app_state = MagicMock()
        s = AppSettings(llm_mapping_enabled=False)
        manager.apply_to_app_state(s, app_state)
        assert app_state.llm_mapping_enabled is False

    def test_apply_to_app_state_calls_set_app_settings(self, manager: SettingsManager) -> None:
        app_state = MagicMock()
        s = AppSettings()
        manager.apply_to_app_state(s, app_state)
        app_state.set_app_settings.assert_called_once_with(s)
