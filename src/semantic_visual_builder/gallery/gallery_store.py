"""Load gallery items from the gallery config file."""

from __future__ import annotations

import json
import logging
from pathlib import Path

from .gallery_schema import GalleryItem

_log = logging.getLogger(__name__)


class GalleryStore:
    def __init__(self, gallery_path: Path) -> None:
        self.gallery_path = gallery_path

    def load_items(self) -> list[GalleryItem]:
        """Load all gallery items from the JSON config. Returns empty list on error."""
        if not self.gallery_path.exists():
            _log.warning("Gallery config not found: %s", self.gallery_path)
            return []
        try:
            data = json.loads(self.gallery_path.read_text(encoding="utf-8"))
            items = data if isinstance(data, list) else data.get("items", [])
            return [GalleryItem.from_dict(item) for item in items if isinstance(item, dict)]
        except Exception as exc:
            _log.warning("Could not load gallery items: %s", exc)
            return []
