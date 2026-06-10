"""Persist AppSettings as a JSON file."""

from __future__ import annotations

import json
import logging
from pathlib import Path

from .settings_schema import AppSettings

_log = logging.getLogger(__name__)


class SettingsStore:
    def __init__(self, settings_path: Path) -> None:
        self.settings_path = settings_path

    def load(self) -> AppSettings:
        """Load settings from disk. Returns defaults if file is missing or corrupt."""
        if not self.settings_path.exists():
            return AppSettings()
        try:
            data = json.loads(self.settings_path.read_text(encoding="utf-8"))
            return AppSettings.from_dict(data)
        except Exception as exc:
            _log.warning("Settings file could not be loaded (%s). Using defaults.", exc)
            return AppSettings()

    def save(self, settings: AppSettings) -> Path:
        """Write settings to disk as pretty JSON."""
        self.settings_path.parent.mkdir(parents=True, exist_ok=True)
        with self.settings_path.open("w", encoding="utf-8") as handle:
            json.dump(settings.to_dict(), handle, indent=2, ensure_ascii=False)
            handle.write("\n")
        return self.settings_path
