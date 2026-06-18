"""Logic-only controller for the settings dialog UI."""

from __future__ import annotations

from dataclasses import dataclass, field

from semantic_visual_builder.settings.settings_schema import AppSettings
from semantic_visual_builder.settings.settings_store import SettingsStore

_SUPPORTED_RENDERERS = ("plotly", "mermaid")


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
            setattr(self._settings, field_name, _coerce_field(field_name, value))
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
            f"Ollama URL: {s.ollama_base_url}",
            f"Model: {s.default_ollama_model or '(none)'}",
            f"Generation timeout: {s.generation_timeout_seconds:.0f}s",
            f"Renderer: {s.default_renderer}",
            f"LLM mapping: {'on' if s.llm_mapping_enabled else 'off'}",
            f"Local renderer assets: {'on' if s.prefer_local_renderer_assets else 'off'}",
            f"Open preview after generation: {'on' if s.open_preview_after_generation else 'off'}",
            f"Export dir: {s.default_export_dir or '(default)'}",
            f"Debug: {'on' if s.debug_mode else 'off'}",
        ]
        return "\n".join(lines)


def _coerce_field(field_name: str, value: object) -> object:
    if field_name == "generation_timeout_seconds":
        try:
            timeout = float(value)  # type: ignore[arg-type]
        except (TypeError, ValueError):
            return value
        return timeout
    if field_name == "ollama_base_url":
        return str(value).strip()
    return value


def _validate_field(field_name: str, value: object) -> list[str]:
    if field_name == "default_renderer" and value not in set(_SUPPORTED_RENDERERS):
        return [f"Unknown renderer: {value!r}. Choose from: {', '.join(_SUPPORTED_RENDERERS)}"]
    if field_name == "ollama_base_url":
        url = str(value or "").strip()
        if not url:
            return ["Ollama URL must not be empty."]
        if not url.startswith(("http://", "https://")):
            return [f"Ollama URL must start with http:// or https://: {url!r}"]
    if field_name == "generation_timeout_seconds":
        try:
            timeout = float(value)  # type: ignore[arg-type]
        except (TypeError, ValueError):
            return [f"Generation timeout must be a number: {value!r}"]
        if timeout <= 0:
            return [f"Generation timeout must be greater than 0: {timeout}"]
    return []


def _validate_settings(settings: AppSettings) -> list[str]:
    errors: list[str] = []
    if settings.default_renderer not in set(_SUPPORTED_RENDERERS):
        errors.append(f"Unknown renderer: {settings.default_renderer!r}")
    if not settings.ollama_base_url or not settings.ollama_base_url.startswith(("http://", "https://")):
        errors.append("Ollama URL must be a valid http(s) URL.")
    if settings.generation_timeout_seconds <= 0:
        errors.append("Generation timeout must be greater than 0.")
    return errors
