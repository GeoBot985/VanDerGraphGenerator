"""Validate recipe skeletons."""

from __future__ import annotations

from typing import Any

from semantic_visual_builder.data.data_profiler import DatasetProfile
from semantic_visual_builder.validation.validation_result import ValidationResult

from .recipe_compatibility import RecipeCompatibilityChecker
from .recipe_migration import RecipeMigration
from .recipe_schema import VisualRecipe


class RecipeValidator:
    """Recipe validation and compatibility checks."""

    allowed_renderers = {"plotly", "chartjs", "mermaid"}
    blocked_tokens = {
        "__import__",
        "eval",
        "exec",
        "subprocess",
        "os.system",
        "<script",
        "javascript:",
    }

    def __init__(self) -> None:
        self.compatibility_checker = RecipeCompatibilityChecker()
        self.migration = RecipeMigration()

    def validate_recipe(self, recipe: VisualRecipe) -> ValidationResult:
        result = ValidationResult()
        metadata = recipe.metadata
        if not metadata.recipe_id.strip():
            result.add_error("metadata.recipe_id must not be blank.")
        if not metadata.recipe_name.strip():
            result.add_error("metadata.recipe_name must not be blank.")
        if not metadata.schema_version.strip():
            result.add_error("metadata.schema_version must not be blank.")
        if metadata.schema_version != "2.0":
            result.add_error("Only schema_version 2.0 is supported for new recipes.")
        if not recipe.expected_fields:
            result.add_error("expected_fields must not be empty.")
        if (
            not isinstance(recipe.visual_plan_template, dict)
            or not recipe.visual_plan_template
        ):
            result.add_error("visual_plan_template must be present.")
        renderer_name = recipe.renderer.renderer if recipe.renderer else None
        if renderer_name and renderer_name not in self.allowed_renderers:
            result.add_error(f"Renderer '{renderer_name}' is not supported.")
        self._scan_for_suspicious_content(recipe.to_dict(), result)
        return result

    def validate_recipe_dict(self, raw: dict[str, Any]) -> ValidationResult:
        try:
            migrated = self.migration.migrate_to_current(raw)
        except NotImplementedError as exc:
            result = ValidationResult()
            result.add_error(str(exc))
            return result
        try:
            recipe = VisualRecipe.from_dict(migrated)
        except Exception as exc:
            result = ValidationResult()
            result.add_error(f"Recipe could not be parsed: {exc}")
            return result
        return self.validate_recipe(recipe)

    def validate_against_dataset(
        self,
        recipe: VisualRecipe,
        dataset_profile: DatasetProfile,
    ) -> ValidationResult:
        report = self.compatibility_checker.check_compatibility(recipe, dataset_profile)
        result = ValidationResult()
        for message in report.errors:
            result.add_error(message)
        for message in report.warnings:
            result.add_warning(message)
        for match in report.field_matches:
            result.add_info(
                f"Matched {match.expected_role}: {match.expected_field} -> "
                f"{match.matched_field or 'unmatched'}"
            )
        return result

    def compatibility_report(
        self, recipe: VisualRecipe, dataset_profile: DatasetProfile
    ) -> ValidationResult:
        return self.validate_against_dataset(recipe, dataset_profile)

    def _scan_for_suspicious_content(
        self, value: Any, result: ValidationResult
    ) -> None:
        if isinstance(value, dict):
            for key, item in value.items():
                self._scan_for_suspicious_content(key, result)
                self._scan_for_suspicious_content(item, result)
            return
        if isinstance(value, list):
            for item in value:
                self._scan_for_suspicious_content(item, result)
            return
        if not isinstance(value, str):
            return
        text = value.lower()
        if any(token in text for token in self.blocked_tokens):
            result.add_error(f"Suspicious content detected in recipe: {value}")
