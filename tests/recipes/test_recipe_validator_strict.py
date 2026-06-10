"""Strict recipe validator tests."""

from semantic_visual_builder.recipes.recipe_schema import (
    RecipeFieldExpectation,
    VisualRecipe,
)
from semantic_visual_builder.recipes.recipe_validator import RecipeValidator


def test_valid_v2_recipe_passes() -> None:
    recipe = VisualRecipe(
        recipe_name="Amount by Region",
        schema_version="2.0",
        visual_plan={"visual_kind": "chart"},
        expected_fields=[RecipeFieldExpectation(role="category", field_name="Region")],
        renderer="plotly",
    )

    result = RecipeValidator().validate_recipe(recipe)

    assert result.is_valid is True


def test_missing_metadata_fails() -> None:
    recipe = VisualRecipe(
        recipe_name="",
        schema_version="2.0",
        visual_plan={"visual_kind": "chart"},
    )

    result = RecipeValidator().validate_recipe(recipe)

    assert result.is_valid is False


def test_missing_visual_plan_template_fails() -> None:
    recipe = VisualRecipe(
        recipe_name="Bad",
        schema_version="2.0",
        visual_plan={},
    )

    result = RecipeValidator().validate_recipe(recipe)

    assert result.is_valid is False


def test_unsupported_renderer_fails() -> None:
    recipe = VisualRecipe(
        recipe_name="Bad",
        schema_version="2.0",
        visual_plan={"visual_kind": "chart"},
        expected_fields=[RecipeFieldExpectation(role="category", field_name="Region")],
        renderer="python",
    )

    result = RecipeValidator().validate_recipe(recipe)

    assert result.is_valid is False


def test_suspicious_content_fails() -> None:
    recipe = VisualRecipe(
        recipe_name="Bad",
        schema_version="2.0",
        visual_plan={"visual_kind": "chart", "notes": "<script>alert(1)</script>"},
        expected_fields=[RecipeFieldExpectation(role="category", field_name="Region")],
        renderer="plotly",
    )

    result = RecipeValidator().validate_recipe(recipe)

    assert result.is_valid is False
