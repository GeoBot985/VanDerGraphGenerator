"""Logic-only controller for the gallery panel UI."""

from __future__ import annotations

from dataclasses import dataclass, field

from semantic_visual_builder.gallery.gallery_runner import GalleryRunner
from semantic_visual_builder.gallery.gallery_schema import GalleryItem


@dataclass
class GalleryPanelController:
    """Manages gallery state and loads items into app_state without Tkinter."""

    items: list[GalleryItem] = field(default_factory=list)
    runner: GalleryRunner = field(default_factory=GalleryRunner)
    _active_item: GalleryItem | None = None

    def set_items(self, items: list[GalleryItem]) -> None:
        self.items = list(items)
        self._active_item = None

    def select_item(self, item_id: str) -> GalleryItem | None:
        for item in self.items:
            if item.item_id == item_id:
                self._active_item = item
                return item
        return None

    def active_item(self) -> GalleryItem | None:
        return self._active_item

    def run_active(self, app_state: object) -> list[str]:
        if self._active_item is None:
            return ["No gallery item selected."]
        return self.runner.run_gallery_item(self._active_item, app_state)

    def items_list_text(self) -> str:
        if not self.items:
            return "No gallery items loaded."
        lines = []
        for item in self.items:
            marker = "* " if self._active_item and self._active_item.item_id == item.item_id else "  "
            lines.append(f"{marker}[{item.item_id}] {item.title}")
        return "\n".join(lines)

    def active_item_text(self) -> str:
        item = self._active_item
        if item is None:
            return "No item selected."
        parts = [f"Title: {item.title}", f"Description: {item.description}"]
        if item.expected_chart_type:
            parts.append(f"Chart type: {item.expected_chart_type}")
        if item.expected_diagram_type:
            parts.append(f"Diagram type: {item.expected_diagram_type}")
        if item.prompt:
            parts.append(f"Prompt: {item.prompt}")
        if item.sample_dataset_path:
            parts.append(f"Dataset: {item.sample_dataset_path}")
        if item.sample_recipe_path:
            parts.append(f"Recipe: {item.sample_recipe_path}")
        return "\n".join(parts)
