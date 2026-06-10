"""Persist visual recipes as JSON files."""

from __future__ import annotations

import json
import re
from pathlib import Path

from .recipe_migration import RecipeMigration
from .recipe_schema import VisualRecipe
from .recipe_validator import RecipeValidator


class RecipeStore:
    """Store and retrieve recipe JSON files."""

    def __init__(self, recipes_dir: Path):
        self.recipes_dir = recipes_dir
        self.recipes_dir.mkdir(parents=True, exist_ok=True)
        self.validator = RecipeValidator()
        self.migration = RecipeMigration()

    def save_recipe(self, recipe: VisualRecipe) -> Path:
        path = self.recipes_dir / f"{self._safe_name(recipe.recipe_name)}.recipe.json"
        payload = recipe.to_dict()
        with path.open("w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2, ensure_ascii=False)
            handle.write("\n")
        return path

    def load_recipe(self, path: Path) -> VisualRecipe:
        with path.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
        migrated = self.migration.migrate_to_current(data)
        recipe = VisualRecipe.from_dict(migrated)
        validation = self.validator.validate_recipe(recipe)
        if not validation.is_valid:
            errors = "; ".join(message.message for message in validation.messages)
            raise ValueError(f"Invalid recipe file: {errors}")
        return recipe

    def list_recipes(self) -> list[Path]:
        return sorted(self.recipes_dir.rglob("*.recipe.json"))

    def _safe_name(self, name: str) -> str:
        safe = re.sub(r"[^A-Za-z0-9._-]+", "_", name.strip()).strip("._-")
        return safe or "recipe"
