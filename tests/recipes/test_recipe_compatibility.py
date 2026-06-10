"""Recipe compatibility tests."""

from semantic_visual_builder.data.data_profiler import ColumnProfile, DatasetProfile
from semantic_visual_builder.recipes.recipe_builder import RecipeBuilder
from semantic_visual_builder.recipes.recipe_validator import RecipeValidator
from semantic_visual_builder.planning.visual_plan_schema import DataRole, VisualPlan


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
    result = RecipeValidator().compatibility_report(recipe, _profile())
    assert result.is_valid is False


def test_compatibility_report_can_be_accessed() -> None:
    result = RecipeValidator().compatibility_report(_recipe(), _profile())
    assert result.is_valid is True
