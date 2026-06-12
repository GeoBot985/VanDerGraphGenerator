"""Tests for StyleImportExport."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from semantic_visual_builder.styles.style_import_export import StyleImportExport
from semantic_visual_builder.styles.style_schema import (
    ColourPalette,
    StyleMetadata,
    StyleProfile,
)
from semantic_visual_builder.styles.style_store import StyleStore


def _make_profile(style_id: str = "test_export") -> StyleProfile:
    return StyleProfile(
        metadata=StyleMetadata(
            style_id=style_id,
            style_name="Test Export",
            schema_version="1.0",
        ),
        palette=ColourPalette(primary="#1f4e79", secondary="#5b9bd5"),
        supported_visual_kinds=["chart"],
        supported_renderers=["plotly"],
    )


def _make_store(tmp_path: Path) -> StyleStore:
    user_dir = tmp_path / "user_styles"
    builtin_dir = tmp_path / "builtin_styles"
    user_dir.mkdir(parents=True, exist_ok=True)
    builtin_dir.mkdir(parents=True, exist_ok=True)
    return StyleStore(user_styles_dir=user_dir, builtin_styles_dir=builtin_dir)


class TestExportStyle:
    def test_export_writes_json_file(self, tmp_path: Path) -> None:
        ie = StyleImportExport()
        profile = _make_profile()
        target = tmp_path / "test_export.style.json"
        result_path = ie.export_style(profile, target)
        assert result_path.exists()

    def test_export_pretty_prints_json(self, tmp_path: Path) -> None:
        ie = StyleImportExport()
        profile = _make_profile()
        target = tmp_path / "test.style.json"
        ie.export_style(profile, target)
        raw = target.read_text(encoding="utf-8")
        assert "\n" in raw

    def test_exported_content_round_trips(self, tmp_path: Path) -> None:
        ie = StyleImportExport()
        profile = _make_profile()
        target = tmp_path / "round.style.json"
        ie.export_style(profile, target)
        data = json.loads(target.read_text(encoding="utf-8"))
        assert data["metadata"]["style_id"] == "test_export"


class TestImportStyle:
    def test_valid_import_saves_to_store(self, tmp_path: Path) -> None:
        ie = StyleImportExport()
        store = _make_store(tmp_path)
        profile = _make_profile("my_import")
        source = tmp_path / "my_import.style.json"
        ie.export_style(profile, source)
        imported = ie.import_style(source, store)
        assert imported.style_id == "my_import"
        assert (store.user_styles_dir / "my_import.style.json").exists()

    def test_invalid_style_raises_value_error(self, tmp_path: Path) -> None:
        ie = StyleImportExport()
        store = _make_store(tmp_path)
        bad = tmp_path / "bad.style.json"
        bad.write_text(
            json.dumps({"metadata": {"style_id": "", "style_name": ""}}),
            encoding="utf-8",
        )
        with pytest.raises(ValueError, match="invalid"):
            ie.import_style(bad, store)

    def test_builtin_overwrite_is_blocked(self, tmp_path: Path) -> None:
        ie = StyleImportExport()
        builtin_dir = tmp_path / "builtins"
        user_dir = tmp_path / "user"
        builtin_dir.mkdir()
        user_dir.mkdir()
        profile = _make_profile("corporate_blue")
        builtin_path = builtin_dir / "corporate_blue.style.json"
        ie.export_style(profile, builtin_path)
        store = StyleStore(user_styles_dir=user_dir, builtin_styles_dir=builtin_dir)
        source = tmp_path / "attempt_overwrite.style.json"
        ie.export_style(profile, source)
        with pytest.raises(ValueError, match="built-in"):
            ie.import_style(source, store)

    def test_duplicate_user_style_blocked_without_overwrite(self, tmp_path: Path) -> None:
        ie = StyleImportExport()
        store = _make_store(tmp_path)
        profile = _make_profile("dup_style")
        source = tmp_path / "dup_style.style.json"
        ie.export_style(profile, source)
        ie.import_style(source, store)
        with pytest.raises(ValueError, match="already exists"):
            ie.import_style(source, store, overwrite=False)
