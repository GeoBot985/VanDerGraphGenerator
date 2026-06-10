"""Recipe mapping tests."""

from semantic_visual_builder.data.data_profiler import ColumnProfile, DatasetProfile
from semantic_visual_builder.recipes.recipe_mapping import RecipeFieldMapper
from semantic_visual_builder.recipes.recipe_schema import (
    RecipeFieldExpectation,
    RecipeMetadata,
    VisualRecipe,
)


def _profile() -> DatasetProfile:
    return DatasetProfile(
        row_count=8,
        column_count=4,
        columns=[
            ColumnProfile("Province", "object", "categorical", 0, 0.0, 4, ["Gauteng"]),
            ColumnProfile("Value", "float64", "numeric", 0, 0.0, 8, ["1.0"]),
            ColumnProfile(
                "TxnDate", "datetime64[ns]", "datetime", 0, 0.0, 8, ["2024-01-01"]
            ),
            ColumnProfile("Outcome", "object", "categorical", 0, 0.0, 2, ["Failed"]),
        ],
    )


def _recipe() -> VisualRecipe:
    return VisualRecipe(
        metadata=RecipeMetadata(
            recipe_id="amount_by_region", recipe_name="Amount by Region"
        ),
        expected_fields=[
            RecipeFieldExpectation(
                role="category", field_name="Region", aliases=["Province"]
            ),
            RecipeFieldExpectation(
                role="measure", field_name="Amount", aliases=["Value"]
            ),
            RecipeFieldExpectation(
                role="x", field_name="TransactionDate", aliases=["TxnDate"]
            ),
        ],
        visual_plan_template={"visual_kind": "chart"},
    )


def test_exact_and_alias_mapping() -> None:
    mappings = RecipeFieldMapper().propose_mappings(_recipe(), _profile())

    assert mappings["Region"] == "Province"
    assert mappings["Amount"] == "Value"
    assert mappings["TransactionDate"] == "TxnDate"
