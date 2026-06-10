"""CSV loading helpers."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd


@dataclass
class LoadedDataset:
    """A loaded CSV dataset."""

    path: Path
    dataframe: pd.DataFrame


class CsvLoader:
    """Load CSV files into pandas dataframes."""

    def load(self, path: Path) -> LoadedDataset:
        if not path.exists():
            raise FileNotFoundError(f"CSV file not found: {path}")
        if path.suffix.lower() != ".csv":
            raise ValueError(f"Unsupported file type: {path.suffix}")
        dataframe = pd.read_csv(path)
        return LoadedDataset(path=path, dataframe=dataframe)
