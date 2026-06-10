"""Export result models."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class ExportResult:
    success: bool
    path: Path | None = None
    export_type: str | None = None
    warnings: list[str] = field(default_factory=list)
    error: str | None = None
