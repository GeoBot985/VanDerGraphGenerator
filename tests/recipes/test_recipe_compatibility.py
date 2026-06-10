"""Recipe compatibility tests."""

from semantic_visual_builder.data.data_profiler import ColumnProfile, DatasetProfile
from semantic_visual_builder.planning.visual_plan_schema import DataRole, VisualPlan
from semantic_visual_builder.recipes.recipe_builder import RecipeBuilder
from semantic_visual_builder.recipes.recipe_compatibility import (
    RecipeCompatibilityChecker,
)
from semantic_visual_builder.recipes.recipe_validator import RecipeValidator


def _profile() -> DatasetProfile:
    return DatasetProfile(
        row_count=10,
        column_count=2,
        columns=[
            ColumnProfile("Region", "object", "categorical", 0, 0.0, 4, ["Gauteng"]),
            ColumnProfile("Amount", "float64", "numeric", 0, 0.0, 10, ["1.0"]),
        ],
    )


def _recipe():
    plan = VisualPlan(
        visual_kind="chart",
        intent="compare_categories",
        chart_type="bar",
        data_roles=[
            DataRole(role="category", field="Region"),
            DataRole(role="measure", field="Amount", aggregation="sum"),
        ],
    )
    return RecipeBuilder().build_from_current_plan("Amount by Region", plan, _profile())


def test_compatibility_report_lists_missing_fields() -> None:
    recipe = _recipe()
    recipe.expected_fields[0].field_name = "Status"
    report = RecipeCompatibilityChecker().check_compatibility(recipe, _profile())
    assert report.can_apply is False
    assert report.errors


def test_compatibility_report_can_be_accessed() -> None:
    result = RecipeValidator().compatibility_report(_recipe(), _profile())
    assert result.is_valid is True


def test_alias_match_scores_high() -> None:
    recipe = _recipe()
    recipe.expected_fields[0].field_name = "Region"
    recipe.expected_fields[0].aliases = ["Province"]
    alias_profile = DatasetProfile(
        row_count=10,
        column_count=2,
        columns=[
            ColumnProfile("Province", "object", "categorical", 0, 0.0, 4, ["Gauteng"]),
            ColumnProfile("Amount", "float64", "numeric", 0, 0.0, 10, ["1.0"]),
        ],
    )
    report = RecipeCompatibilityChecker().check_compatibility(recipe, alias_profile)
    assert report.field_matches[0].score >= 0.85
