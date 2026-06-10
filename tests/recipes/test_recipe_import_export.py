"""Recipe import/export tests."""

import pytest

from semantic_visual_builder.recipes.recipe_import_export import RecipeImportExport
from semantic_visual_builder.recipes.recipe_schema import (
    RecipeFieldExpectation,
    VisualRecipe,
)
from semantic_visual_builder.recipes.recipe_store import RecipeStore


def _recipe() -> VisualRecipe:
    return VisualRecipe(
        recipe_name="Amount by Region",
        schema_version="2.0",
        visual_plan={"visual_kind": "chart"},
        expected_fields=[RecipeFieldExpectation(role="category", field_name="Region")],
        renderer="plotly",
    )


def test_recipe_exports_to_json(tmp_path) -> None:
    path = RecipeImportExport().export_recipe(
        _recipe(), tmp_path / "exported.recipe.json"
    )

    assert path.exists()
    assert path.read_text(encoding="utf-8").startswith('{\n  "metadata"')


def test_imported_recipe_validates_before_saving(tmp_path) -> None:
    source = tmp_path / "imported.recipe.json"
    source.write_text(
        """{
  "metadata": {
    "recipe_id": "amount_by_region",
    "recipe_name": "Amount by Region",
    "schema_version": "2.0"
  },
  "expected_fields": [
    {"role": "category", "field_name": "Region", "required": true}
  ],
  "visual_plan_template": {"visual_kind": "chart"},
  "renderer": {"renderer": "plotly"}
}
""",
        encoding="utf-8",
    )
    store = RecipeStore(tmp_path / "store")

    saved = RecipeImportExport().import_recipe(source, store)

    assert saved.exists()


def test_invalid_import_is_rejected(tmp_path) -> None:
    source = tmp_path / "bad.recipe.json"
    source.write_text(
        """{
  "metadata": {
    "recipe_id": "bad",
    "recipe_name": "Bad",
    "schema_version": "2.0"
  },
  "expected_fields": [],
  "visual_plan_template": {
    "visual_kind": "chart",
    "danger": "<script>alert(1)</script>"
  }
}
""",
        encoding="utf-8",
    )
    store = RecipeStore(tmp_path / "store")

    with pytest.raises(ValueError):
        RecipeImportExport().import_recipe(source, store)
