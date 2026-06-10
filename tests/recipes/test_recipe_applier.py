"""Recipe applier tests."""

from semantic_visual_builder.data.data_profiler import ColumnProfile, DatasetProfile
from semantic_visual_builder.recipes.recipe_applier import RecipeApplier
from semantic_visual_builder.recipes.recipe_builder import RecipeBuilder
from semantic_visual_builder.planning.visual_plan_schema import DataRole, VisualPlan


def _profile() -> DatasetProfile:
    return DatasetProfile(
        row_count=10,
        column_count=3,
        columns=[
            ColumnProfile("TransactionDate", "datetime64[ns]", "datetime", 0, 0.0, 10, ["2024-01-01"]),
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


def test_exact_field_matches_apply_successfully() -> None:
    result = RecipeApplier().apply_recipe(_recipe(), _profile())
    assert result.success is True
    assert result.visual_plan is not None


def test_missing_required_field_fails() -> None:
    recipe = _recipe()
    recipe.expected_fields[0].field_name = "Missing"
    result = RecipeApplier().apply_recipe(recipe, _profile())
    assert result.success is False
    assert result.errors


def test_case_insensitive_field_match_works() -> None:
    recipe = _recipe()
    recipe.expected_fields[0].field_name = "region"
    result = RecipeApplier().apply_recipe(recipe, _profile())
    assert result.success is True
    assert result.field_mappings["region"] == "Region"


def test_applied_recipe_produces_valid_visual_plan() -> None:
    result = RecipeApplier().apply_recipe(_recipe(), _profile())
    assert result.visual_plan is not None
    assert result.visual_plan.metadata.is_preview_stale is True
