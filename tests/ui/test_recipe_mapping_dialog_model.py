"""Recipe mapping dialog model tests."""

from semantic_visual_builder.recipes.recipe_compatibility import (
    FieldMatch,
    RecipeCompatibilityReport,
)
from semantic_visual_builder.ui.recipe_mapping_dialog import (
    build_recipe_mapping_dialog_model,
)


def test_mapping_dialog_model_uses_report_rows() -> None:
    report = RecipeCompatibilityReport(
        recipe_name="Amount by Region",
        overall_score=0.85,
        can_apply=True,
        field_matches=[
            FieldMatch(
                expected_field="Region",
                expected_role="category",
                expected_semantic_type="categorical",
                matched_field="Province",
                matched_semantic_type="categorical",
                score=0.85,
                match_reason="alias match",
            )
        ],
    )

    model = build_recipe_mapping_dialog_model(report)

    assert model.can_apply is True
    assert model.rows[0].suggested_dataset_field == "Province"
