"""Persist visual recipes as JSON files."""

from __future__ import annotations

import json
import re
from dataclasses import asdict
from pathlib import Path

from .recipe_schema import RecipeFieldExpectation, VisualRecipe


class RecipeStore:
    """Store and retrieve recipe JSON files."""

    def __init__(self, recipes_dir: Path):
        self.recipes_dir = recipes_dir
        self.recipes_dir.mkdir(parents=True, exist_ok=True)

    def save_recipe(self, recipe: VisualRecipe) -> Path:
        path = self.recipes_dir / f"{self._safe_name(recipe.recipe_name)}.recipe.json"
        payload = asdict(recipe)
        with path.open("w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2, ensure_ascii=False)
        return path

    def load_recipe(self, path: Path) -> VisualRecipe:
        with path.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
        expected_fields = [
            RecipeFieldExpectation(**item)
            for item in data.get("expected_fields", [])
            if isinstance(item, dict)
        ]
        return VisualRecipe(
            recipe_name=data["recipe_name"],
            schema_version=data["schema_version"],
            visual_plan=data["visual_plan"],
            expected_fields=expected_fields,
            renderer=data.get("renderer"),
            description=data.get("description"),
            created_at=data.get("created_at"),
        )

    def list_recipes(self) -> list[Path]:
        return sorted(self.recipes_dir.glob("*.recipe.json"))

    def _safe_name(self, name: str) -> str:
        safe = re.sub(r"[^A-Za-z0-9._-]+", "_", name.strip()).strip("._-")
        return safe or "recipe"
