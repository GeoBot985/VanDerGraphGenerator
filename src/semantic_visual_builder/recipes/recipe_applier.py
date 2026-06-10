"""Apply recipes to datasets."""

from __future__ import annotations

from dataclasses import dataclass, field

from semantic_visual_builder.data.data_profiler import DatasetProfile
from semantic_visual_builder.planning.visual_plan import set_role, visual_plan_from_dict
from semantic_visual_builder.planning.visual_plan_schema import VisualPlan
from semantic_visual_builder.utils.text_sanitize import normalize_name

from .recipe_schema import VisualRecipe


@dataclass
class RecipeApplicationResult:
    success: bool
    visual_plan: VisualPlan | None = None
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    field_mappings: dict[str, str] = field(default_factory=dict)


class RecipeApplier:
    """Apply a recipe to a compatible dataset profile."""

    def apply_recipe(
        self,
        recipe: VisualRecipe,
        dataset_profile: DatasetProfile,
    ) -> RecipeApplicationResult:
        dataset_fields = {column.name: column.semantic_type for column in dataset_profile.columns}
        normalized_lookup = {normalize_name(name): name for name in dataset_fields}
        warnings: list[str] = []
        errors: list[str] = []
        field_mappings: dict[str, str] = {}

        for expected in recipe.expected_fields:
            if expected.field_name == "row_count":
                field_mappings[expected.field_name] = "row_count"
                continue
            mapped = self._match_field(expected.field_name, dataset_fields, normalized_lookup)
            if mapped is None:
                if expected.required:
                    errors.append(f"Required field '{expected.field_name}' for role '{expected.role}' could not be mapped.")
                continue
            field_mappings[expected.field_name] = mapped
            actual_type = dataset_fields.get(mapped)
            if expected.semantic_type and actual_type not in {expected.semantic_type, "unknown"}:
                warnings.append(
                    f"Field '{mapped}' is {actual_type} but recipe expected {expected.semantic_type}."
                )

        if errors:
            return RecipeApplicationResult(success=False, warnings=warnings, errors=errors, field_mappings=field_mappings)

        plan = visual_plan_from_dict(recipe.visual_plan)
        for expected in recipe.expected_fields:
            mapped = field_mappings.get(expected.field_name)
            if mapped is None:
                continue
            set_role(plan, expected.role, mapped)
        plan.render_target.renderer = recipe.renderer or plan.render_target.renderer
        plan.metadata.created_from = "recipe"
        plan.metadata.is_preview_stale = True
        return RecipeApplicationResult(success=True, visual_plan=plan, warnings=warnings, field_mappings=field_mappings)

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
        if normalized in normalized_lookup:
            return normalized_lookup[normalized]
        for candidate in dataset_fields:
            if normalize_name(candidate) == normalized:
                return candidate
        return None
