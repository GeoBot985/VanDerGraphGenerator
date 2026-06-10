"""Validate recipe skeletons."""

from __future__ import annotations

from semantic_visual_builder.data.data_profiler import DatasetProfile
from semantic_visual_builder.utils.text_sanitize import normalize_name
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
        return self.compatibility_report(recipe, dataset_profile)

    def compatibility_report(self, recipe: VisualRecipe, dataset_profile: DatasetProfile) -> ValidationResult:
        result = self.validate_recipe(recipe)
        dataset_fields = {column.name: column.semantic_type for column in dataset_profile.columns}
        normalized_lookup = {normalize_name(name): name for name in dataset_fields}
        for expected in recipe.expected_fields:
            if expected.field_name == "row_count":
                result.add_info(f"Matched {expected.role}: row_count -> virtual row count")
                continue
            match_name = self._match_field(expected.field_name, dataset_fields, normalized_lookup)
            if match_name is None:
                if expected.required:
                    result.add_error(f"Expected field '{expected.field_name}' for role '{expected.role}' was not found.")
                else:
                    result.add_warning(f"Expected field '{expected.field_name}' for role '{expected.role}' was not found.")
                continue
            actual_type = dataset_fields.get(match_name)
            result.add_info(f"Matched {expected.role}: {expected.field_name} -> {match_name}")
            if expected.semantic_type and actual_type not in {expected.semantic_type, "unknown"}:
                result.add_warning(
                    f"Field '{match_name}' is {actual_type} but recipe expected {expected.semantic_type}."
                )
        return result

    def _match_field(
        self,
        field_name: str,
        dataset_fields: dict[str, str],
        normalized_lookup: dict[str, str],
    ) -> str | None:
        if field_name in dataset_fields:
            return field_name
        lower_lookup = {name.lower(): name for name in dataset_fields}
        if field_name.lower() in lower_lookup:
            return lower_lookup[field_name.lower()]
        normalized = normalize_name(field_name)
        return normalized_lookup.get(normalized)
