"""UI-neutral sheet selection model for Excel workbooks."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass
class SheetSelection:
    workbook_path: Path
    available_sheets: list[str]
    selected_sheet: str | None = None

    def select(self, sheet_name: str) -> None:
        """Set the selected sheet, raising ValueError if not available."""
        if sheet_name not in self.available_sheets:
            raise ValueError(
                f"Sheet '{sheet_name}' is not available. "
                f"Available: {', '.join(self.available_sheets)}"
            )
        self.selected_sheet = sheet_name

    def select_first(self) -> None:
        """Auto-select the first available sheet."""
        if self.available_sheets:
            self.selected_sheet = self.available_sheets[0]
