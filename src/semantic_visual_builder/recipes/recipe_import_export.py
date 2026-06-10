"""Recipe import/export helpers."""

from __future__ import annotations

import json
from pathlib import Path

from .recipe_schema import VisualRecipe
from .recipe_store import RecipeStore
from .recipe_validator import RecipeValidator


class RecipeImportExport:
    def __init__(self) -> None:
        self.validator = RecipeValidator()

    def export_recipe(self, recipe: VisualRecipe, target_path: Path) -> Path:
        target_path.parent.mkdir(parents=True, exist_ok=True)
        target_path.write_text(
            json.dumps(recipe.to_dict(), indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        return target_path

    def import_recipe(self, source_path: Path, recipe_store: RecipeStore) -> Path:
        raw = source_path.read_text(encoding="utf-8")
        data = json.loads(raw)
        validation = self.validator.validate_recipe_dict(data)
        if not validation.is_valid:
            errors = "; ".join(message.message for message in validation.messages)
            raise ValueError(f"Recipe import rejected: {errors}")
        recipe = VisualRecipe.from_dict(data)
        return recipe_store.save_recipe(recipe)
