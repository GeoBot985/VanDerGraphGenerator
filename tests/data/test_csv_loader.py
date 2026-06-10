"""CSV loader tests."""

from pathlib import Path

import pytest

from semantic_visual_builder.data.csv_loader import CsvLoader


def test_loads_sample_transactions() -> None:
    root = Path(__file__).resolve().parents[2]
    loaded = CsvLoader().load(root / "assets" / "samples" / "sample_transactions.csv")
    assert loaded.dataframe.shape == (5, 4)


def test_rejects_non_csv_extension(tmp_path: Path) -> None:
    path = tmp_path / "sample.txt"
    path.write_text("value\n1", encoding="utf-8")
    with pytest.raises(ValueError):
        CsvLoader().load(path)


def test_missing_file_raises(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        CsvLoader().load(tmp_path / "missing.csv")
