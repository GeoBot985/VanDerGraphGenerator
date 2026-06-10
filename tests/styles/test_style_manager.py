"""Style manager tests."""

import json
from pathlib import Path

import pytest

from semantic_visual_builder.styles.style_manager import StyleManager
from semantic_visual_builder.styles.style_schema import (
    ChartStyle,
    ColourPalette,
    StyleMetadata,
    StyleProfile,
    TypographyStyle,
)
from semantic_visual_builder.styles.style_store import StyleStore
from semantic_visual_builder.styles.style_validator import StyleValidator


def _style() -> StyleProfile:
    return StyleProfile(
        metadata=StyleMetadata(style_id="sample_style", style_name="Sample Style"),
        palette=ColourPalette(primary="#1f4e79"),
        typography=TypographyStyle(font_family="Arial"),
        chart=ChartStyle(background="#ffffff"),
    )


def test_style_manager_lists_and_finds_styles(tmp_path: Path) -> None:
    store = StyleStore(tmp_path / "user", tmp_path / "builtin")
    builtin_path = store.builtin_styles_dir / "sample.style.json"
    builtin_path.write_text(json.dumps(_style().to_dict()), encoding="utf-8")
    manager = StyleManager(store, StyleValidator())

    styles = manager.list_styles()

    assert len(styles) == 1
    assert manager.get_style_by_id("sample_style") is not None


def test_style_manager_saves_valid_style_and_rejects_invalid(tmp_path: Path) -> None:
    manager = StyleManager(
        StyleStore(tmp_path / "user", tmp_path / "builtin"), StyleValidator()
    )
    saved = manager.save_style(_style())

    assert saved.exists()
    assert saved.name == "sample_style.style.json"

    bad_style = _style()
    bad_style.metadata.schema_version = "2.0"

    with pytest.raises(ValueError):
        manager.save_style(bad_style)
