"""Recipe mapping review dialog helpers."""

from __future__ import annotations

from dataclasses import dataclass, field

from semantic_visual_builder.recipes.recipe_compatibility import (
    RecipeCompatibilityReport,
)


@dataclass
class RecipeMappingRow:
    recipe_field: str
    role: str
    suggested_dataset_field: str | None
    score: float
    reason: str


@dataclass
class RecipeMappingDialogModel:
    rows: list[RecipeMappingRow] = field(default_factory=list)
    can_apply: bool = False


def build_recipe_mapping_dialog_model(
    report: RecipeCompatibilityReport,
) -> RecipeMappingDialogModel:
    rows = [
        RecipeMappingRow(
            recipe_field=match.expected_field,
            role=match.expected_role,
            suggested_dataset_field=match.matched_field,
            score=match.score,
            reason=match.match_reason,
        )
        for match in report.field_matches
    ]
    return RecipeMappingDialogModel(rows=rows, can_apply=report.can_apply)
