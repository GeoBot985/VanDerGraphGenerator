"""Tests for GalleryItem schema."""

from __future__ import annotations

from semantic_visual_builder.gallery.gallery_schema import GalleryItem


class TestGalleryItem:
    def test_from_dict_minimal(self) -> None:
        item = GalleryItem.from_dict({"item_id": "x", "title": "X", "description": "desc"})
        assert item.item_id == "x"
        assert item.title == "X"

    def test_from_dict_all_fields(self) -> None:
        data = {
            "item_id": "sales",
            "title": "Sales Chart",
            "description": "Monthly sales",
            "sample_dataset_path": "assets/data.csv",
            "sample_recipe_path": "assets/recipe.json",
            "sample_style_id": "corporate_blue",
            "prompt": "Show sales",
            "expected_visual_kind": "chart",
            "expected_chart_type": "bar",
            "expected_diagram_type": None,
        }
        item = GalleryItem.from_dict(data)
        assert item.sample_dataset_path == "assets/data.csv"
        assert item.expected_chart_type == "bar"

    def test_to_dict_roundtrip(self) -> None:
        item = GalleryItem(
            item_id="test1",
            title="Test",
            description="A test item",
            prompt="Show me a bar chart",
        )
        d = item.to_dict()
        restored = GalleryItem.from_dict(d)
        assert restored.item_id == "test1"
        assert restored.prompt == "Show me a bar chart"

    def test_missing_optional_fields_are_none(self) -> None:
        item = GalleryItem.from_dict({"item_id": "y", "title": "Y", "description": "d"})
        assert item.sample_dataset_path is None
        assert item.prompt is None

    def test_item_id_coerced_to_str(self) -> None:
        item = GalleryItem.from_dict({"item_id": 42, "title": "T", "description": "D"})
        assert item.item_id == "42"
