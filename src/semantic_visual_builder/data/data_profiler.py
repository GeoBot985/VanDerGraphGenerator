"""Deterministic dataframe profiling helpers."""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


@dataclass
class ColumnProfile:
    name: str
    dtype: str
    semantic_type: str
    null_count: int
    null_percent: float
    unique_count: int
    sample_values: list[str]


@dataclass
class DatasetProfile:
    row_count: int
    column_count: int
    columns: list[ColumnProfile]


class DataProfiler:
    """Build a lightweight deterministic profile."""

    def profile(self, dataframe: pd.DataFrame) -> DatasetProfile:
        columns: list[ColumnProfile] = []
        row_count = len(dataframe)
        for name in dataframe.columns:
            series = dataframe[name]
            non_null = series.dropna()
            semantic_type = self._detect_semantic_type(series)
            null_count = int(series.isna().sum())
            null_percent = (null_count / row_count * 100.0) if row_count else 0.0
            columns.append(
                ColumnProfile(
                    name=str(name),
                    dtype=str(series.dtype),
                    semantic_type=semantic_type,
                    null_count=null_count,
                    null_percent=null_percent,
                    unique_count=int(series.nunique(dropna=True)),
                    sample_values=[str(value) for value in non_null.head(3).tolist()],
                )
            )
        return DatasetProfile(row_count=row_count, column_count=len(dataframe.columns), columns=columns)

    def _detect_semantic_type(self, series: pd.Series) -> str:
        if pd.api.types.is_bool_dtype(series):
            return "boolean"
        if pd.api.types.is_numeric_dtype(series):
            return "numeric"
        if pd.api.types.is_object_dtype(series) or pd.api.types.is_string_dtype(series):
            values = series.dropna().astype(str)
            if not len(values):
                return "unknown"
            unique_ratio = values.nunique() / len(values)
            long_values = values.map(len).mean() > 40 if len(values) else False
            boolean_like = set(values.str.lower().unique()).issubset({"true", "false", "yes", "no", "0", "1"})
            if boolean_like:
                return "boolean"
            name_hint = any(token in str(series.name).lower() for token in ("date", "time", "timestamp"))
            parsed = pd.to_datetime(values, errors="coerce", format="mixed")
            parsed_ratio = parsed.notna().sum() / len(values)
            if name_hint or parsed_ratio >= 0.8:
                return "datetime"
            if unique_ratio <= 0.8:
                return "categorical"
            if long_values or unique_ratio > 0.5:
                return "text"
        return "unknown"
