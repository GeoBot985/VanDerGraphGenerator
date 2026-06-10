"""Tests for SettingsStore."""

from __future__ import annotations

from pathlib import Path

import pytest

from semantic_visual_builder.settings.settings_schema import AppSettings
from semantic_visual_builder.settings.settings_store import SettingsStore


@pytest.fixture()
def store(tmp_path: Path) -> SettingsStore:
    return SettingsStore(tmp_path / "settings.json")


class TestSettingsStore:
    def test_load_missing_returns_defaults(self, store: SettingsStore) -> None:
        s = store.load()
        assert s.default_renderer == "plotly"

    def test_save_creates_file(self, store: SettingsStore) -> None:
        store.save(AppSettings())
        assert store.settings_path.exists()

    def test_roundtrip(self, store: SettingsStore) -> None:
        s = AppSettings(default_ollama_model="mistral", debug_mode=True)
        store.save(s)
        loaded = store.load()
        assert loaded.default_ollama_model == "mistral"
        assert loaded.debug_mode is True

    def test_corrupt_file_returns_defaults(self, store: SettingsStore) -> None:
        store.settings_path.parent.mkdir(parents=True, exist_ok=True)
        store.settings_path.write_text("not json!", encoding="utf-8")
        s = store.load()
        assert s.default_renderer == "plotly"

    def test_save_returns_path(self, store: SettingsStore) -> None:
        returned = store.save(AppSettings())
        assert returned == store.settings_path
