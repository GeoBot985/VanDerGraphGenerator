"""Tests for GalleryRunner."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock


from semantic_visual_builder.gallery.gallery_runner import GalleryRunner
from semantic_visual_builder.gallery.gallery_schema import GalleryItem
from semantic_visual_builder.gallery.gallery_store import GalleryStore


def _make_item(**kwargs) -> GalleryItem:
    defaults = {"item_id": "test", "title": "Test", "description": "desc"}
    defaults.update(kwargs)
    return GalleryItem(**defaults)


class TestGalleryRunner:
    def test_run_with_no_paths_returns_messages(self) -> None:
        item = _make_item()
        app_state = MagicMock(spec=[])
        messages = GalleryRunner().run_gallery_item(item, app_state)
        assert isinstance(messages, list)

    def test_missing_dataset_reported(self, tmp_path: Path) -> None:
        item = _make_item(sample_dataset_path=str(tmp_path / "missing.csv"))
        app_state = MagicMock()
        messages = GalleryRunner().run_gallery_item(item, app_state)
        assert any("not found" in m.lower() or "could not" in m.lower() for m in messages)

    def test_missing_recipe_reported(self, tmp_path: Path) -> None:
        item = _make_item(sample_recipe_path=str(tmp_path / "missing.json"))
        app_state = MagicMock()
        messages = GalleryRunner().run_gallery_item(item, app_state)
        assert any("not found" in m.lower() or "could not" in m.lower() for m in messages)

    def test_set_active_gallery_item_called(self) -> None:
        item = _make_item()
        app_state = MagicMock()
        GalleryRunner().run_gallery_item(item, app_state)
        app_state.set_active_gallery_item.assert_called_once_with(item)

    def test_set_active_gallery_item_not_called_if_no_method(self) -> None:
        item = _make_item()
        app_state = MagicMock(spec=[])
        messages = GalleryRunner().run_gallery_item(item, app_state)
        assert isinstance(messages, list)


class TestGalleryStore:
    def test_load_from_json_list(self, tmp_path: Path) -> None:
        data = [
            {"item_id": "a", "title": "A", "description": "desc A"},
            {"item_id": "b", "title": "B", "description": "desc B"},
        ]
        p = tmp_path / "gallery.json"
        p.write_text(json.dumps(data), encoding="utf-8")
        items = GalleryStore(p).load_items()
        assert len(items) == 2
        assert items[0].item_id == "a"

    def test_load_from_json_object_with_items_key(self, tmp_path: Path) -> None:
        data = {"items": [{"item_id": "x", "title": "X", "description": "d"}]}
        p = tmp_path / "gallery.json"
        p.write_text(json.dumps(data), encoding="utf-8")
        items = GalleryStore(p).load_items()
        assert len(items) == 1
        assert items[0].item_id == "x"

    def test_missing_file_returns_empty(self, tmp_path: Path) -> None:
        items = GalleryStore(tmp_path / "missing.json").load_items()
        assert items == []

    def test_corrupt_file_returns_empty(self, tmp_path: Path) -> None:
        p = tmp_path / "bad.json"
        p.write_text("not json", encoding="utf-8")
        items = GalleryStore(p).load_items()
        assert items == []
