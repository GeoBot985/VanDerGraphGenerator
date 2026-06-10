"""Tests for ExcelLoader."""

from __future__ import annotations

import io
from pathlib import Path
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from semantic_visual_builder.data.excel_loader import ExcelLoader, ExcelWorkbookInfo, LoadedExcelDataset


def _make_excel_bytes(sheets: dict[str, pd.DataFrame]) -> bytes:
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        for name, df in sheets.items():
            df.to_excel(writer, sheet_name=name, index=False)
    return buf.getvalue()


@pytest.fixture()
def simple_xlsx(tmp_path: Path) -> Path:
    p = tmp_path / "test.xlsx"
    df = pd.DataFrame({"month": ["Jan", "Feb"], "sales": [100, 200]})
    p.write_bytes(_make_excel_bytes({"Sheet1": df}))
    return p


@pytest.fixture()
def multi_sheet_xlsx(tmp_path: Path) -> Path:
    p = tmp_path / "multi.xlsx"
    df1 = pd.DataFrame({"a": [1, 2]})
    df2 = pd.DataFrame({"b": [3, 4]})
    p.write_bytes(_make_excel_bytes({"Alpha": df1, "Beta": df2}))
    return p


class TestExcelLoaderInspect:
    def test_returns_sheet_names(self, simple_xlsx: Path) -> None:
        info = ExcelLoader().inspect_workbook(simple_xlsx)
        assert info.sheet_names == ["Sheet1"]

    def test_returns_multiple_sheets(self, multi_sheet_xlsx: Path) -> None:
        info = ExcelLoader().inspect_workbook(multi_sheet_xlsx)
        assert set(info.sheet_names) == {"Alpha", "Beta"}

    def test_path_stored_in_info(self, simple_xlsx: Path) -> None:
        info = ExcelLoader().inspect_workbook(simple_xlsx)
        assert info.path == simple_xlsx

    def test_missing_file_raises(self, tmp_path: Path) -> None:
        with pytest.raises(FileNotFoundError):
            ExcelLoader().inspect_workbook(tmp_path / "missing.xlsx")

    def test_wrong_extension_raises(self, tmp_path: Path) -> None:
        p = tmp_path / "data.csv"
        p.write_text("a,b\n1,2")
        with pytest.raises(ValueError, match="Unsupported Excel format"):
            ExcelLoader().inspect_workbook(p)


class TestExcelLoaderLoad:
    def test_loads_correct_sheet(self, simple_xlsx: Path) -> None:
        result = ExcelLoader().load_sheet(simple_xlsx, "Sheet1")
        assert isinstance(result, LoadedExcelDataset)
        assert list(result.dataframe.columns) == ["month", "sales"]

    def test_dataframe_rows(self, simple_xlsx: Path) -> None:
        result = ExcelLoader().load_sheet(simple_xlsx, "Sheet1")
        assert len(result.dataframe) == 2

    def test_sheet_name_stored(self, simple_xlsx: Path) -> None:
        result = ExcelLoader().load_sheet(simple_xlsx, "Sheet1")
        assert result.sheet_name == "Sheet1"

    def test_unknown_sheet_raises(self, simple_xlsx: Path) -> None:
        with pytest.raises(ValueError, match="not found in workbook"):
            ExcelLoader().load_sheet(simple_xlsx, "NoSuchSheet")

    def test_multi_sheet_select_second(self, multi_sheet_xlsx: Path) -> None:
        result = ExcelLoader().load_sheet(multi_sheet_xlsx, "Beta")
        assert "b" in result.dataframe.columns

    def test_column_names_stripped(self, tmp_path: Path) -> None:
        p = tmp_path / "spaced.xlsx"
        df = pd.DataFrame({" name ": ["x"], " value ": [1]})
        p.write_bytes(_make_excel_bytes({"Data": df}))
        result = ExcelLoader().load_sheet(p, "Data")
        assert "name" in result.dataframe.columns
        assert "value" in result.dataframe.columns
