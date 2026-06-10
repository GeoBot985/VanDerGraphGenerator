"""Coordinate recipe storage, compatibility, mapping, and application."""

from __future__ import annotations

from pathlib import Path

from semantic_visual_builder.data.data_profiler import DatasetProfile

from .recipe_applier import RecipeApplicationResult, RecipeApplier
from .recipe_compatibility import RecipeCompatibilityChecker, RecipeCompatibilityReport
from .recipe_mapping import RecipeFieldMapper
from .recipe_schema import VisualRecipe
from .recipe_store import RecipeStore
from .recipe_validator import RecipeValidator


class RecipeManager:
    def __init__(
        self,
        recipe_store: RecipeStore,
        recipe_validator: RecipeValidator,
        compatibility_checker: RecipeCompatibilityChecker,
        field_mapper: RecipeFieldMapper,
        recipe_applier: RecipeApplier,
    ):
        self.recipe_store = recipe_store
        self.recipe_validator = recipe_validator
        self.compatibility_checker = compatibility_checker
        self.field_mapper = field_mapper
        self.recipe_applier = recipe_applier

    def list_available_recipes(self) -> list[VisualRecipe]:
        return [self.load_recipe(path) for path in self.recipe_store.list_recipes()]

    def load_recipe(self, path: Path) -> VisualRecipe:
        return self.recipe_store.load_recipe(path)

    def save_recipe(self, recipe: VisualRecipe) -> Path:
        validation = self.recipe_validator.validate_recipe(recipe)
        if not validation.is_valid:
            errors = "; ".join(message.message for message in validation.messages)
            raise ValueError(errors)
        return self.recipe_store.save_recipe(recipe)

    def check_recipe_for_dataset(
        self,
        recipe: VisualRecipe,
        dataset_profile: DatasetProfile,
    ) -> RecipeCompatibilityReport:
        return self.compatibility_checker.check_compatibility(recipe, dataset_profile)

    def propose_and_apply(
        self,
        recipe: VisualRecipe,
        dataset_profile: DatasetProfile,
    ) -> RecipeApplicationResult:
        mappings = self.field_mapper.propose_mappings(recipe, dataset_profile)
        return self.recipe_applier.apply_recipe(recipe, dataset_profile, mappings)

    def set_recipe_default_style(
        self,
        recipe: VisualRecipe,
        style_id: str,
        style_name: str | None = None,
    ) -> Path:
        recipe.metadata.default_style_profile_id = style_id
        recipe.metadata.default_style_profile_name = style_name
        return self.save_recipe(recipe)

    def clear_recipe_default_style(self, recipe: VisualRecipe) -> Path:
        recipe.metadata.default_style_profile_id = None
        recipe.metadata.default_style_profile_name = None
        return self.save_recipe(recipe)
