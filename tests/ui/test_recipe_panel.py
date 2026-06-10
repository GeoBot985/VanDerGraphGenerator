"""Recipe panel tests."""

from semantic_visual_builder.planning.visual_plan_schema import VisualPlan
from semantic_visual_builder.recipes.recipe_schema import RecipeFieldExpectation, VisualRecipe
from semantic_visual_builder.state.app_state import AppState
from semantic_visual_builder.ui.recipe_panel import RecipePanel


def test_recipe_panel_can_display_active_recipe_state() -> None:
    state = AppState()
    panel = RecipePanel()
    assert "No active recipe" in panel.active_recipe_text(state)
    state.set_active_recipe(
        VisualRecipe(
            recipe_name="Amount by Region",
            schema_version="1.0",
            visual_plan={"visual_kind": "chart"},
            expected_fields=[RecipeFieldExpectation(role="category", field_name="Region")],
        )
    )
    assert "Amount by Region" in panel.active_recipe_text(state)
