"""Persist style profiles as JSON files."""

from __future__ import annotations

import json
import re
from pathlib import Path

from .style_schema import StyleProfile


class StyleStore:
    def __init__(self, user_styles_dir: Path, builtin_styles_dir: Path):
        self.user_styles_dir = user_styles_dir
        self.builtin_styles_dir = builtin_styles_dir
        self.user_styles_dir.mkdir(parents=True, exist_ok=True)
        self.builtin_styles_dir.mkdir(parents=True, exist_ok=True)

    def list_builtin_styles(self) -> list[Path]:
        return sorted(self.builtin_styles_dir.glob("*.style.json"))

    def list_user_styles(self) -> list[Path]:
        return sorted(self.user_styles_dir.glob("*.style.json"))

    def load_style(self, path: Path) -> StyleProfile:
        with path.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
        return StyleProfile.from_dict(data)

    def save_user_style(self, style: StyleProfile) -> Path:
        path = self.user_styles_dir / f"{self._safe_name(style.style_id)}.style.json"
        payload = style.to_dict()
        with path.open("w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2, ensure_ascii=False)
            handle.write("\n")
        return path

    def delete_user_style(self, style_id: str) -> bool:
        path = self.user_styles_dir / f"{self._safe_name(style_id)}.style.json"
        if not path.exists():
            return False
        path.unlink()
        return True

    def _safe_name(self, name: str) -> str:
        safe = re.sub(r"[^A-Za-z0-9._-]+", "_", name.strip()).strip("._-")
        return safe or "style"
