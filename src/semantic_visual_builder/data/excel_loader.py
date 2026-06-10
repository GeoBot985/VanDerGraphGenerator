"""Excel (.xlsx) loading helpers."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd


_SUPPORTED_EXTENSIONS = {".xlsx"}


@dataclass
class ExcelWorkbookInfo:
    path: Path
    sheet_names: list[str]


@dataclass
class LoadedExcelDataset:
    path: Path
    sheet_name: str
    dataframe: pd.DataFrame


class ExcelLoader:
    """Load Excel workbooks into pandas DataFrames.

    Only .xlsx is supported. Macro workbooks, password-protected files,
    and binary .xlsb format are not supported.
    """

    def inspect_workbook(self, path: Path) -> ExcelWorkbookInfo:
        """Return metadata about an Excel workbook without loading any sheet data."""
        self._check_path(path)
        workbook = pd.ExcelFile(path, engine="openpyxl")
        return ExcelWorkbookInfo(path=path, sheet_names=list(workbook.sheet_names))

    def load_sheet(self, path: Path, sheet_name: str) -> LoadedExcelDataset:
        """Load a named sheet from an Excel workbook into a DataFrame."""
        self._check_path(path)
        info = self.inspect_workbook(path)
        if sheet_name not in info.sheet_names:
            raise ValueError(
                f"Sheet '{sheet_name}' not found in workbook. "
                f"Available sheets: {', '.join(info.sheet_names)}"
            )
        dataframe = pd.read_excel(path, sheet_name=sheet_name, engine="openpyxl")
        if dataframe.empty:
            raise ValueError(f"Sheet '{sheet_name}' is empty.")
        dataframe.columns = [str(col).strip() for col in dataframe.columns]
        return LoadedExcelDataset(path=path, sheet_name=sheet_name, dataframe=dataframe)

    def _check_path(self, path: Path) -> None:
        if not path.exists():
            raise FileNotFoundError(f"Excel file not found: {path}")
        if path.suffix.lower() not in _SUPPORTED_EXTENSIONS:
            raise ValueError(
                f"Unsupported Excel format: {path.suffix}. "
                f"Supported: {', '.join(sorted(_SUPPORTED_EXTENSIONS))}"
            )
