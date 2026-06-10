"""Recipe schema and builder tests."""

from semantic_visual_builder.data.data_profiler import ColumnProfile, DatasetProfile
from semantic_visual_builder.planning.visual_plan_schema import DataRole, VisualPlan
from semantic_visual_builder.recipes.recipe_builder import RecipeBuilder
from semantic_visual_builder.recipes.recipe_schema import (
    RecipeMetadata,
    RecipeRenderer,
    RecipeStyle,
    VisualRecipe,
)


def _profile() -> DatasetProfile:
    return DatasetProfile(
        row_count=10,
        column_count=3,
        columns=[
            ColumnProfile("Region", "object", "categorical", 0, 0.0, 3, ["Gauteng"]),
            ColumnProfile("Amount", "float64", "numeric", 0, 0.0, 10, ["1.0"]),
            ColumnProfile(
                "TransactionDate",
                "datetime64[ns]",
                "datetime",
                0,
                0.0,
                10,
                ["2024-01-01"],
            ),
        ],
    )


def test_recipe_can_be_built_from_current_visual_plan() -> None:
    plan = VisualPlan(
        visual_kind="chart",
        intent="compare_categories",
        chart_type="bar",
        data_roles=[
            DataRole(role="category", field="Region"),
            DataRole(role="measure", field="Amount", aggregation="sum"),
        ],
    )
    recipe = RecipeBuilder().build_from_current_plan(
        "Total by region", plan, _profile()
    )
    assert recipe.metadata.recipe_name == "Total by region"
    assert recipe.schema_version == "2.0"
    assert recipe.expected_fields[0].field_name == "Region"
    assert recipe.expected_fields[1].semantic_type == "numeric"


def test_recipe_v2_dataclasses_instantiate() -> None:
    recipe = VisualRecipe(
        metadata=RecipeMetadata(
            recipe_id="amount_by_region", recipe_name="Amount by Region"
        ),
        expected_fields=[],
        visual_plan_template={"visual_kind": "chart"},
        style=RecipeStyle(title="Amount by Region"),
        renderer=RecipeRenderer(renderer="plotly", output_type="plotly_json"),
    )
    assert recipe.metadata.recipe_id == "amount_by_region"
    assert recipe.style.title == "Amount by Region"
    assert recipe.renderer is not None
