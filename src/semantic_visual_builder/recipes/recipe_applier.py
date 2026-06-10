"""Apply recipes to datasets."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field
from typing import Any

from semantic_visual_builder.data.data_profiler import DatasetProfile
from semantic_visual_builder.planning.visual_plan import visual_plan_from_dict
from semantic_visual_builder.planning.visual_plan_schema import VisualPlan

from .recipe_compatibility import RecipeCompatibilityChecker, RecipeCompatibilityReport
from .recipe_mapping import RecipeFieldMapper
from .recipe_schema import VisualRecipe
from .recipe_validator import RecipeValidator


@dataclass
class RecipeApplicationResult:
    success: bool
    visual_plan: VisualPlan | None = None
    compatibility_report: RecipeCompatibilityReport | None = None
    field_mappings: dict[str, str] = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    default_style_profile_id: str | None = None
    default_style_profile_name: str | None = None


class RecipeApplier:
    """Apply a recipe to a compatible dataset profile."""

    def __init__(self) -> None:
        self.validator = RecipeValidator()
        self.compatibility_checker = RecipeCompatibilityChecker()
        self.field_mapper = RecipeFieldMapper()

    def apply_recipe(
        self,
        recipe: VisualRecipe,
        dataset_profile: DatasetProfile,
        field_mappings: dict[str, str] | None = None,
    ) -> RecipeApplicationResult:
        validation = self.validator.validate_recipe(recipe)
        if not validation.is_valid:
            return RecipeApplicationResult(
                success=False,
                errors=[
                    message.message
                    for message in validation.messages
                    if message.severity.value == "error"
                ],
            )

        compatibility = self.compatibility_checker.check_compatibility(
            recipe, dataset_profile
        )
        mappings = dict(
            field_mappings
            or self.field_mapper.propose_mappings(recipe, dataset_profile)
        )
        warnings = list(compatibility.warnings)
        errors: list[str] = []

        for expected in recipe.expected_fields:
            if expected.field_name == "row_count":
                mappings.setdefault("row_count", "row_count")
                continue
            if expected.required and expected.field_name not in mappings:
                errors.append(
                    f"Missing mapping for required field '{expected.field_name}' "
                    f"({expected.role})."
                )

        if errors:
            return RecipeApplicationResult(
                success=False,
                compatibility_report=compatibility,
                field_mappings=mappings,
                warnings=warnings,
                errors=errors,
            )

        placeholder_mappings = self._build_placeholder_mappings(recipe, mappings)
        template = self._substitute_placeholders(
            recipe.visual_plan_template, placeholder_mappings
        )
        plan = visual_plan_from_dict(template)
        self._apply_style(plan, recipe)
        if recipe.renderer is not None:
            plan.render_target.renderer = recipe.renderer.renderer
            plan.render_target.output_format = recipe.renderer.output_type
        plan.metadata.created_from = "recipe"
        plan.metadata.is_preview_stale = True
        plan.notes.extend(note for note in recipe.notes if note not in plan.notes)
        plan.metadata.assumptions = list(plan.metadata.assumptions)
        plan.metadata.pending_questions = list(plan.metadata.pending_questions)

        default_style_id = recipe.metadata.default_style_profile_id
        default_style_name = recipe.metadata.default_style_profile_name
        if default_style_id:
            warnings.append(
                f"This recipe has a default style: {default_style_name or default_style_id}. "
                "Apply it now?"
            )
        return RecipeApplicationResult(
            success=True,
            visual_plan=plan,
            compatibility_report=compatibility,
            field_mappings=mappings,
            warnings=warnings,
            default_style_profile_id=default_style_id,
            default_style_profile_name=default_style_name,
        )

    def _substitute_placeholders(self, data: Any, mappings: dict[str, str]) -> Any:
        if isinstance(data, dict):
            return {
                key: self._substitute_placeholders(value, mappings)
                for key, value in data.items()
            }
        if isinstance(data, list):
            return [self._substitute_placeholders(item, mappings) for item in data]
        if isinstance(data, str):
            updated = data
            for expected, actual in mappings.items():
                updated = updated.replace(f"{{{{{expected}}}}}", actual)
            return updated
        return deepcopy(data)

    def _build_placeholder_mappings(
        self, recipe: VisualRecipe, mappings: dict[str, str]
    ) -> dict[str, str]:
        placeholder_mappings = dict(mappings)
        for expected in recipe.expected_fields:
            actual = mappings.get(expected.field_name)
            if actual is None:
                continue
            placeholder_mappings.setdefault(expected.role, actual)
            placeholder_mappings.setdefault(expected.field_name, actual)
        return placeholder_mappings

    def _apply_style(self, plan: VisualPlan, recipe: VisualRecipe) -> None:
        if recipe.style.title is not None:
            plan.style.title = recipe.style.title
        if recipe.style.subtitle is not None:
            plan.style.subtitle = recipe.style.subtitle
        if recipe.style.colour_scheme is not None:
            plan.style.colour_scheme = recipe.style.colour_scheme
        if recipe.style.highlights:
            plan.style.highlights = deepcopy(recipe.style.highlights)
        if recipe.style.labels:
            plan.style.labels = deepcopy(recipe.style.labels)
        if recipe.style.orientation is not None:
            plan.style.orientation = recipe.style.orientation
