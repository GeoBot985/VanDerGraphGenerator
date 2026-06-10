"""Dataset context helpers."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .csv_loader import LoadedDataset
from .data_profiler import DatasetProfile


@dataclass
class DatasetSourceInfo:
    source_type: str
    path: Path | None = None
    sheet_name: str | None = None


@dataclass
class DatasetContext:
    loaded_dataset: LoadedDataset | None = None
    profile: DatasetProfile | None = None
    source_info: DatasetSourceInfo | None = None

    @property
    def has_dataset(self) -> bool:
        return self.loaded_dataset is not None
