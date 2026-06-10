"""Recipe store tests."""

from semantic_visual_builder.recipes.recipe_schema import RecipeFieldExpectation, VisualRecipe
from semantic_visual_builder.recipes.recipe_store import RecipeStore


def test_recipe_saves_to_json_file(tmp_path) -> None:
    store = RecipeStore(tmp_path)
    recipe = VisualRecipe(
        recipe_name="Total Amount by Region",
        schema_version="1.0",
        visual_plan={"visual_kind": "chart"},
        expected_fields=[RecipeFieldExpectation(role="category", field_name="Region")],
        renderer="plotly",
    )
    path = store.save_recipe(recipe)
    assert path.exists()
    assert path.name == "Total_Amount_by_Region.recipe.json"


def test_recipe_loads_from_json_file(tmp_path) -> None:
    store = RecipeStore(tmp_path)
    recipe = VisualRecipe(
        recipe_name="Load Me",
        schema_version="1.0",
        visual_plan={"visual_kind": "chart"},
    )
    path = store.save_recipe(recipe)
    loaded = store.load_recipe(path)
    assert loaded.recipe_name == "Load Me"
    assert loaded.schema_version == "1.0"


def test_recipe_listing_returns_saved_files(tmp_path) -> None:
    store = RecipeStore(tmp_path)
    store.save_recipe(VisualRecipe(recipe_name="One", schema_version="1.0", visual_plan={"visual_kind": "chart"}))
    assert store.list_recipes()
