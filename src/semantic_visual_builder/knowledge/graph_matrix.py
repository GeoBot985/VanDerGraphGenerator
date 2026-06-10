"""Graph matrix loading helpers."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from semantic_visual_builder.utils.json_utils import load_json


@dataclass
class GraphMatrix:
    """Structured graph matrix data."""

    raw: dict[str, Any]

    def list_intents(self) -> list[str]:
        return [item.get("intent", "") for item in self.raw.get("intents", []) if isinstance(item, dict) and item.get("intent")]


class GraphMatrixLoader:
    """Load the graph matrix seed file."""

    def __init__(self, matrix_path: Path):
        self.matrix_path = matrix_path

    def load(self) -> GraphMatrix:
        return GraphMatrix(raw=load_json(self.matrix_path))
