"""Validate recipe skeletons."""

from __future__ import annotations

from semantic_visual_builder.data.data_profiler import DatasetProfile
from semantic_visual_builder.validation.validation_result import ValidationResult

from .recipe_schema import VisualRecipe


class RecipeValidator:
    """Basic recipe validation."""

    def validate_recipe(self, recipe: VisualRecipe) -> ValidationResult:
        result = ValidationResult()
        if not recipe.recipe_name.strip():
            result.add_error("recipe_name must not be blank.")
        if not recipe.schema_version.strip():
            result.add_error("schema_version must not be blank.")
        if not isinstance(recipe.visual_plan, dict) or not recipe.visual_plan:
            result.add_error("visual_plan must be present.")
        return result

    def validate_against_dataset(
        self,
        recipe: VisualRecipe,
        dataset_profile: DatasetProfile,
    ) -> ValidationResult:
        result = self.validate_recipe(recipe)
        dataset_fields = {column.name: column.semantic_type for column in dataset_profile.columns}
        for expected in recipe.expected_fields:
            if expected.required and expected.field_name not in dataset_fields:
                result.add_error(f"Expected field '{expected.field_name}' for role '{expected.role}' was not found.")
                continue
            if expected.semantic_type and dataset_fields.get(expected.field_name) not in {expected.semantic_type, "unknown"}:
                result.add_warning(
                    f"Field '{expected.field_name}' is {dataset_fields.get(expected.field_name)} but recipe expected {expected.semantic_type}."
                )
        return result
