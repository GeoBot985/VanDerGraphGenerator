"""Recipe validator tests."""

from semantic_visual_builder.data.data_profiler import ColumnProfile, DatasetProfile
from semantic_visual_builder.recipes.recipe_schema import (
    RecipeFieldExpectation,
    VisualRecipe,
)
from semantic_visual_builder.recipes.recipe_validator import RecipeValidator


def _profile() -> DatasetProfile:
    return DatasetProfile(
        row_count=8,
        column_count=2,
        columns=[
            ColumnProfile("Region", "object", "categorical", 0, 0.0, 3, ["Gauteng"]),
            ColumnProfile("Amount", "float64", "numeric", 0, 0.0, 8, ["1.0"]),
        ],
    )


def test_recipe_validates_against_matching_dataset_profile() -> None:
    recipe = VisualRecipe(
        recipe_name="Matched",
        schema_version="2.0",
        visual_plan={"visual_kind": "chart"},
        expected_fields=[
            RecipeFieldExpectation(
                role="category", field_name="Region", semantic_type="categorical"
            )
        ],
    )
    result = RecipeValidator().validate_against_dataset(recipe, _profile())
    assert result.is_valid is True


def test_recipe_reports_missing_expected_field() -> None:
    recipe = VisualRecipe(
        recipe_name="Missing",
        schema_version="2.0",
        visual_plan={"visual_kind": "chart"},
        expected_fields=[
            RecipeFieldExpectation(
                role="category", field_name="Status", semantic_type="categorical"
            )
        ],
    )
    result = RecipeValidator().validate_against_dataset(recipe, _profile())
    assert result.is_valid is False


def test_recipe_reports_semantic_type_mismatch_warning() -> None:
    recipe = VisualRecipe(
        recipe_name="Mismatch",
        schema_version="2.0",
        visual_plan={"visual_kind": "chart"},
        expected_fields=[
            RecipeFieldExpectation(
                role="category", field_name="Region", semantic_type="numeric"
            )
        ],
    )
    result = RecipeValidator().validate_against_dataset(recipe, _profile())
    assert result.is_valid is True
    assert result.messages
