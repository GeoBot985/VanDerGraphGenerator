"""Coordinate settings load/save and app state application."""

from __future__ import annotations

from pathlib import Path

from .settings_schema import AppSettings
from .settings_store import SettingsStore


class SettingsManager:
    def __init__(self, store: SettingsStore) -> None:
        self.store = store

    def load_settings(self) -> AppSettings:
        return self.store.load()

    def save_settings(self, settings: AppSettings) -> Path:
        return self.store.save(settings)

    def apply_to_app_state(self, settings: AppSettings, app_state: object) -> None:
        """Apply loaded settings to app state where applicable."""
        if hasattr(app_state, "llm_mapping_enabled"):
            app_state.llm_mapping_enabled = settings.llm_mapping_enabled  # type: ignore[union-attr]
        if hasattr(app_state, "set_app_settings"):
            app_state.set_app_settings(settings)  # type: ignore[union-attr]
