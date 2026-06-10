"""Tests for recipe default style integration."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from semantic_visual_builder.recipes.recipe_schema import RecipeMetadata, VisualRecipe


def _make_recipe(
    recipe_id: str = "test_recipe",
    default_style_id: str | None = None,
    default_style_name: str | None = None,
) -> VisualRecipe:
    metadata = RecipeMetadata(
        recipe_id=recipe_id,
        recipe_name="Test Recipe",
        default_style_profile_id=default_style_id,
        default_style_profile_name=default_style_name,
    )
    return VisualRecipe(metadata=metadata)


class TestRecipeDefaultStyleSchema:
    def test_recipe_can_store_default_style_id(self) -> None:
        recipe = _make_recipe(default_style_id="corporate_blue")
        assert recipe.metadata.default_style_profile_id == "corporate_blue"

    def test_recipe_can_store_default_style_name(self) -> None:
        recipe = _make_recipe(
            default_style_id="corporate_blue", default_style_name="Corporate Blue"
        )
        assert recipe.metadata.default_style_profile_name == "Corporate Blue"

    def test_recipe_default_style_none_by_default(self) -> None:
        recipe = _make_recipe()
        assert recipe.metadata.default_style_profile_id is None

    def test_recipe_roundtrips_default_style_via_dict(self) -> None:
        recipe = _make_recipe(
            default_style_id="my_style",
            default_style_name="My Style",
        )
        data = recipe.to_dict()
        restored = VisualRecipe.from_dict(data)
        assert restored.metadata.default_style_profile_id == "my_style"
        assert restored.metadata.default_style_profile_name == "My Style"

    def test_clear_default_style(self) -> None:
        recipe = _make_recipe(default_style_id="some_style")
        recipe.metadata.default_style_profile_id = None
        recipe.metadata.default_style_profile_name = None
        assert recipe.metadata.default_style_profile_id is None


class TestRecipeApplicationResult:
    def test_application_result_has_default_style_fields(self) -> None:
        from semantic_visual_builder.recipes.recipe_applier import RecipeApplicationResult

        result = RecipeApplicationResult(
            success=True,
            default_style_profile_id="corporate_blue",
            default_style_profile_name="Corporate Blue",
        )
        assert result.default_style_profile_id == "corporate_blue"
        assert result.default_style_profile_name == "Corporate Blue"

    def test_application_result_default_style_none_when_not_set(self) -> None:
        from semantic_visual_builder.recipes.recipe_applier import RecipeApplicationResult

        result = RecipeApplicationResult(success=True)
        assert result.default_style_profile_id is None


class TestRecipeManagerDefaultStyle:
    def test_set_recipe_default_style_updates_metadata(self) -> None:
        from semantic_visual_builder.recipes.recipe_manager import RecipeManager

        store = MagicMock()
        store.save_recipe.return_value = Path("test.recipe.json")
        validator = MagicMock()
        validator.validate_recipe.return_value = MagicMock(is_valid=True, messages=[])
        manager = RecipeManager(
            recipe_store=store,
            recipe_validator=validator,
            compatibility_checker=MagicMock(),
            field_mapper=MagicMock(),
            recipe_applier=MagicMock(),
        )
        recipe = _make_recipe()
        manager.set_recipe_default_style(recipe, "corporate_blue", "Corporate Blue")
        assert recipe.metadata.default_style_profile_id == "corporate_blue"
        assert recipe.metadata.default_style_profile_name == "Corporate Blue"

    def test_clear_recipe_default_style(self) -> None:
        from semantic_visual_builder.recipes.recipe_manager import RecipeManager

        store = MagicMock()
        store.save_recipe.return_value = Path("test.recipe.json")
        validator = MagicMock()
        validator.validate_recipe.return_value = MagicMock(is_valid=True, messages=[])
        manager = RecipeManager(
            recipe_store=store,
            recipe_validator=validator,
            compatibility_checker=MagicMock(),
            field_mapper=MagicMock(),
            recipe_applier=MagicMock(),
        )
        recipe = _make_recipe(default_style_id="corporate_blue")
        manager.clear_recipe_default_style(recipe)
        assert recipe.metadata.default_style_profile_id is None
