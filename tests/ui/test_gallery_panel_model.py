"""Tests for GalleryPanelController."""

from __future__ import annotations

from unittest.mock import MagicMock

from semantic_visual_builder.gallery.gallery_schema import GalleryItem
from semantic_visual_builder.ui.gallery_panel import GalleryPanelController


def _item(item_id: str, title: str = "Title") -> GalleryItem:
    return GalleryItem(item_id=item_id, title=title, description="desc")


class TestGalleryPanelController:
    def test_items_list_empty_by_default(self) -> None:
        ctrl = GalleryPanelController()
        assert "No gallery items loaded" in ctrl.items_list_text()

    def test_set_items(self) -> None:
        ctrl = GalleryPanelController()
        ctrl.set_items([_item("a"), _item("b")])
        assert len(ctrl.items) == 2

    def test_select_item_by_id(self) -> None:
        ctrl = GalleryPanelController()
        items = [_item("x"), _item("y")]
        ctrl.set_items(items)
        selected = ctrl.select_item("x")
        assert selected is not None
        assert selected.item_id == "x"

    def test_select_unknown_returns_none(self) -> None:
        ctrl = GalleryPanelController()
        ctrl.set_items([_item("a")])
        assert ctrl.select_item("zzz") is None

    def test_active_item_after_select(self) -> None:
        ctrl = GalleryPanelController()
        ctrl.set_items([_item("q")])
        ctrl.select_item("q")
        assert ctrl.active_item() is not None
        assert ctrl.active_item().item_id == "q"

    def test_run_active_no_selection_returns_message(self) -> None:
        ctrl = GalleryPanelController()
        messages = ctrl.run_active(MagicMock())
        assert any("no" in m.lower() for m in messages)

    def test_items_list_text_shows_ids(self) -> None:
        ctrl = GalleryPanelController()
        ctrl.set_items([_item("a", "Alpha"), _item("b", "Beta")])
        text = ctrl.items_list_text()
        assert "a" in text
        assert "b" in text

    def test_active_item_text_shows_description(self) -> None:
        ctrl = GalleryPanelController()
        ctrl.set_items([GalleryItem(item_id="z", title="Z", description="Zoom")])
        ctrl.select_item("z")
        text = ctrl.active_item_text()
        assert "Zoom" in text

    def test_active_item_text_no_selection(self) -> None:
        ctrl = GalleryPanelController()
        text = ctrl.active_item_text()
        assert "No item selected" in text
