"""Dataset context helpers."""

from __future__ import annotations

from dataclasses import dataclass

from .csv_loader import LoadedDataset
from .data_profiler import DatasetProfile


@dataclass
class DatasetContext:
    loaded_dataset: LoadedDataset | None = None
    profile: DatasetProfile | None = None

    @property
    def has_dataset(self) -> bool:
        return self.loaded_dataset is not None
