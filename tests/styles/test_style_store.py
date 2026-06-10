"""Style store tests."""

import json
from pathlib import Path

from semantic_visual_builder.styles.style_schema import (
    ChartStyle,
    ColourPalette,
    StyleMetadata,
    StyleProfile,
    TypographyStyle,
)
from semantic_visual_builder.styles.style_store import StyleStore


def _style() -> StyleProfile:
    return StyleProfile(
        metadata=StyleMetadata(style_id="sample_style", style_name="Sample Style"),
        palette=ColourPalette(primary="#1f4e79"),
        typography=TypographyStyle(font_family="Arial"),
        chart=ChartStyle(background="#ffffff"),
    )


def test_style_store_saves_loads_and_deletes_user_styles(tmp_path: Path) -> None:
    store = StyleStore(tmp_path / "user", tmp_path / "builtin")
    style = _style()

    saved = store.save_user_style(style)
    assert saved.exists()
    assert saved.name == "sample_style.style.json"
    assert store.list_user_styles() == [saved]

    loaded = store.load_style(saved)
    assert loaded.style_id == "sample_style"
    assert loaded.style_name == "Sample Style"

    assert store.delete_user_style("sample_style") is True
    assert not saved.exists()


def test_style_store_lists_builtin_styles(tmp_path: Path) -> None:
    store = StyleStore(tmp_path / "user", tmp_path / "builtin")
    builtin_path = store.builtin_styles_dir / "sample.style.json"
    builtin_path.write_text(json.dumps(_style().to_dict()), encoding="utf-8")

    assert store.list_builtin_styles() == [builtin_path]
