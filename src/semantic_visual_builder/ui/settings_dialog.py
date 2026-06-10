"""Logic-only controller for the settings dialog UI."""

from __future__ import annotations

from dataclasses import dataclass, field

from semantic_visual_builder.settings.settings_schema import AppSettings
from semantic_visual_builder.settings.settings_store import SettingsStore


@dataclass
class SettingsDialogController:
    """Manages loading/saving settings without any Tkinter dependency."""

    store: SettingsStore
    _settings: AppSettings = field(default_factory=AppSettings)

    def load(self) -> AppSettings:
        self._settings = self.store.load()
        return self._settings

    def current_settings(self) -> AppSettings:
        return self._settings

    def update_field(self, field_name: str, value: object) -> list[str]:
        """Apply a single field update. Returns a list of validation errors."""
        errors = _validate_field(field_name, value)
        if not errors:
            setattr(self._settings, field_name, value)
        return errors

    def save(self) -> tuple[bool, str]:
        """Persist current settings. Returns (success, message)."""
        errors = _validate_settings(self._settings)
        if errors:
            return False, "; ".join(errors)
        try:
            path = self.store.save(self._settings)
            return True, f"Settings saved to {path.name}"
        except Exception as exc:
            return False, f"Save failed: {exc}"

    def reset_to_defaults(self) -> AppSettings:
        self._settings = AppSettings()
        return self._settings

    def summary_text(self) -> str:
        s = self._settings
        lines = [
            f"Model: {s.default_ollama_model or '(none)'}",
            f"Renderer: {s.default_renderer}",
            f"LLM mapping: {'on' if s.llm_mapping_enabled else 'off'}",
            f"Export dir: {s.default_export_dir or '(default)'}",
            f"Debug: {'on' if s.debug_mode else 'off'}",
        ]
        return "\n".join(lines)


def _validate_field(field_name: str, value: object) -> list[str]:
    if field_name == "default_renderer" and value not in {"plotly", "mermaid", "chartjs"}:
        return [f"Unknown renderer: {value!r}"]
    return []


def _validate_settings(settings: AppSettings) -> list[str]:
    errors = []
    if settings.default_renderer not in {"plotly", "mermaid", "chartjs"}:
        errors.append(f"Unknown renderer: {settings.default_renderer!r}")
    return errors
