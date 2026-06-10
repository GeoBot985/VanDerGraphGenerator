"""Tests for AppSettings schema."""

from __future__ import annotations

from semantic_visual_builder.settings.settings_schema import AppSettings


class TestAppSettingsDefaults:
    def test_default_renderer_is_plotly(self) -> None:
        assert AppSettings().default_renderer == "plotly"

    def test_llm_mapping_enabled_default(self) -> None:
        assert AppSettings().llm_mapping_enabled is True

    def test_debug_mode_default_false(self) -> None:
        assert AppSettings().debug_mode is False

    def test_default_model_is_none(self) -> None:
        assert AppSettings().default_ollama_model is None


class TestAppSettingsRoundtrip:
    def test_to_dict_and_back(self) -> None:
        s = AppSettings(
            default_ollama_model="llama3",
            llm_mapping_enabled=False,
            default_renderer="mermaid",
            default_export_dir="/tmp/exports",
            debug_mode=True,
        )
        d = s.to_dict()
        restored = AppSettings.from_dict(d)
        assert restored.default_ollama_model == "llama3"
        assert restored.llm_mapping_enabled is False
        assert restored.default_renderer == "mermaid"
        assert restored.default_export_dir == "/tmp/exports"
        assert restored.debug_mode is True

    def test_from_dict_missing_keys_use_defaults(self) -> None:
        s = AppSettings.from_dict({})
        assert s.default_renderer == "plotly"
        assert s.llm_mapping_enabled is True

    def test_to_dict_has_all_keys(self) -> None:
        keys = set(AppSettings().to_dict().keys())
        expected = {
            "default_ollama_model", "llm_mapping_enabled", "default_renderer",
            "default_export_dir", "prefer_local_renderer_assets",
            "open_preview_after_generation", "default_style_profile_id", "debug_mode",
        }
        assert expected.issubset(keys)
