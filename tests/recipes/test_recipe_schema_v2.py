"""Recipe schema v2 tests."""

from semantic_visual_builder.recipes.recipe_schema import (
    RecipeFieldExpectation,
    RecipeMetadata,
    RecipeRenderer,
    RecipeStyle,
    VisualRecipe,
)


def test_v2_recipe_dataclasses_serialize() -> None:
    recipe = VisualRecipe(
        metadata=RecipeMetadata(
            recipe_id="amount_by_region", recipe_name="Amount by Region"
        ),
        expected_fields=[
            RecipeFieldExpectation(
                role="category",
                field_name="Region",
                semantic_type="categorical",
            )
        ],
        visual_plan_template={"visual_kind": "chart"},
        style=RecipeStyle(title="Amount by Region", colour_scheme="blue"),
        renderer=RecipeRenderer(renderer="plotly", output_type="plotly_json"),
    )

    payload = recipe.to_dict()

    assert payload["metadata"]["schema_version"] == "2.0"
    assert payload["metadata"]["recipe_name"] == "Amount by Region"
    assert payload["expected_fields"][0]["aliases"] == []
    assert payload["style"]["colour_scheme"] == "blue"
    assert payload["renderer"]["renderer"] == "plotly"
