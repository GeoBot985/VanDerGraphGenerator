"""Gallery item schema."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class GalleryItem:
    item_id: str
    title: str
    description: str
    sample_dataset_path: str | None = None
    sample_recipe_path: str | None = None
    sample_style_id: str | None = None
    prompt: str | None = None
    expected_visual_kind: str | None = None
    expected_chart_type: str | None = None
    expected_diagram_type: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "item_id": self.item_id,
            "title": self.title,
            "description": self.description,
            "sample_dataset_path": self.sample_dataset_path,
            "sample_recipe_path": self.sample_recipe_path,
            "sample_style_id": self.sample_style_id,
            "prompt": self.prompt,
            "expected_visual_kind": self.expected_visual_kind,
            "expected_chart_type": self.expected_chart_type,
            "expected_diagram_type": self.expected_diagram_type,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "GalleryItem":
        return cls(
            item_id=str(data.get("item_id", "")),
            title=str(data.get("title", "")),
            description=str(data.get("description", "")),
            sample_dataset_path=data.get("sample_dataset_path"),
            sample_recipe_path=data.get("sample_recipe_path"),
            sample_style_id=data.get("sample_style_id"),
            prompt=data.get("prompt"),
            expected_visual_kind=data.get("expected_visual_kind"),
            expected_chart_type=data.get("expected_chart_type"),
            expected_diagram_type=data.get("expected_diagram_type"),
        )
