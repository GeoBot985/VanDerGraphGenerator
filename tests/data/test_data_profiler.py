"""Data profiler tests."""

from pathlib import Path

from semantic_visual_builder.data.csv_loader import CsvLoader
from semantic_visual_builder.data.data_profiler import DataProfiler


def test_profile_counts_and_types() -> None:
    root = Path(__file__).resolve().parents[2]
    dataframe = CsvLoader().load(root / "assets" / "samples" / "sample_transactions.csv").dataframe
    profile = DataProfiler().profile(dataframe)

    assert profile.row_count == 5
    assert profile.column_count == 4
    types = {column.name: column.semantic_type for column in profile.columns}
    assert types["Amount"] == "numeric"
    assert types["Region"] == "categorical"
    assert types["TransactionDate"] == "datetime"


def test_profile_null_count() -> None:
    import pandas as pd

    dataframe = pd.DataFrame({"a": [1, None, 3]})
    profile = DataProfiler().profile(dataframe)
    assert profile.columns[0].null_count == 1
