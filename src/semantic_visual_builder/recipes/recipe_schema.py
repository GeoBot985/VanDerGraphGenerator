"""Recipe schema models."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class RecipeFieldExpectation:
    role: str
    field_name: str
    semantic_type: str | None = None
    required: bool = True


@dataclass
class VisualRecipe:
    recipe_name: str
    schema_version: str
    visual_plan: dict[str, Any]
    expected_fields: list[RecipeFieldExpectation] = field(default_factory=list)
    renderer: str | None = None
    description: str | None = None
    created_at: str | None = None
