"""Import and export style profiles as .style.json files."""

from __future__ import annotations

import json
from pathlib import Path

from .style_schema import StyleProfile
from .style_store import StyleStore
from .style_validator import StyleValidator


class StyleImportExport:
    def export_style(self, style: StyleProfile, target_path: Path) -> Path:
        """Export a style profile to a .style.json file. Returns the written path."""
        payload = style.to_dict()
        target_path.parent.mkdir(parents=True, exist_ok=True)
        with target_path.open("w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2, ensure_ascii=False)
            handle.write("\n")
        return target_path

    def import_style(
        self,
        source_path: Path,
        style_store: StyleStore,
        overwrite: bool = False,
    ) -> StyleProfile:
        """Import a style profile from a .style.json file.

        Validates before saving. Raises ValueError on invalid style.
        Built-in styles are never overwritten even if overwrite=True.
        """
        with source_path.open("r", encoding="utf-8") as handle:
            data = json.load(handle)

        style = StyleProfile.from_dict(data)
        validator = StyleValidator()
        result = validator.validate_style(style)
        errors = [msg.message for msg in result.messages if msg.severity.value == "error"]
        if errors:
            raise ValueError(f"Imported style is invalid: {'; '.join(errors)}")

        builtin_ids = {
            style_store.load_style(path).style_id
            for path in style_store.list_builtin_styles()
        }
        if style.style_id in builtin_ids:
            raise ValueError(
                f"Cannot overwrite built-in style '{style.style_id}'. Save as a new style instead."
            )

        if not overwrite:
            existing_user = {
                style_store.load_style(path).style_id
                for path in style_store.list_user_styles()
            }
            if style.style_id in existing_user:
                raise ValueError(
                    f"A user style with ID '{style.style_id}' already exists. "
                    "Use overwrite=True to replace it."
                )

        return style_store.save_user_style(style) and style or style
