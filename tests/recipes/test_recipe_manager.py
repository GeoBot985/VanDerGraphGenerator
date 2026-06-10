"""Recipe manager tests."""

from semantic_visual_builder.data.data_profiler import ColumnProfile, DatasetProfile
from semantic_visual_builder.planning.visual_plan_schema import DataRole, VisualPlan
from semantic_visual_builder.recipes.recipe_applier import RecipeApplier
from semantic_visual_builder.recipes.recipe_builder import RecipeBuilder
from semantic_visual_builder.recipes.recipe_compatibility import (
    RecipeCompatibilityChecker,
)
from semantic_visual_builder.recipes.recipe_manager import RecipeManager
from semantic_visual_builder.recipes.recipe_mapping import RecipeFieldMapper
from semantic_visual_builder.recipes.recipe_store import RecipeStore
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


def _plan() -> VisualPlan:
    return VisualPlan(
        visual_kind="chart",
        intent="compare_categories",
        chart_type="bar",
        data_roles=[
            DataRole(role="category", field="Region"),
            DataRole(role="measure", field="Amount", aggregation="sum"),
        ],
    )


def _manager(tmp_path) -> RecipeManager:
    store = RecipeStore(tmp_path)
    return RecipeManager(
        store,
        RecipeValidator(),
        RecipeCompatibilityChecker(),
        RecipeFieldMapper(),
        RecipeApplier(),
    )


def test_save_load_and_list_recipes(tmp_path) -> None:
    manager = _manager(tmp_path)
    recipe = RecipeBuilder().build_from_current_plan(
        "Amount by Region", _plan(), _profile()
    )

    path = manager.save_recipe(recipe)
    loaded = manager.load_recipe(path)

    assert path.exists()
    assert loaded.recipe_name == "Amount by Region"
    assert manager.list_available_recipes()


def test_check_and_apply_recipe(tmp_path) -> None:
    manager = _manager(tmp_path)
    recipe = RecipeBuilder().build_from_current_plan(
        "Amount by Region", _plan(), _profile()
    )

    report = manager.check_recipe_for_dataset(recipe, _profile())
    result = manager.propose_and_apply(recipe, _profile())

    assert report.can_apply is True
    assert result.success is True
    assert result.visual_plan is not None
