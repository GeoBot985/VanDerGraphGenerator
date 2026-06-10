"""LLM mapping result models."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class LlmVisualPlanDraft:
    visual_kind: str
    intent: str
    chart_type: str | None = None
    diagram_type: str | None = None
    roles: dict[str, Any] = field(default_factory=dict)
    filters: list[dict[str, Any]] = field(default_factory=list)
    grouping: list[str] = field(default_factory=list)
    style: dict[str, Any] = field(default_factory=dict)
    renderer: str | None = None
    confidence: float | None = None
    assumptions: list[str] = field(default_factory=list)
    questions: list[str] = field(default_factory=list)
    diagram_nodes: list[dict[str, Any]] = field(default_factory=list)
    diagram_edges: list[dict[str, Any]] = field(default_factory=list)


@dataclass
class LlmMappingResult:
    raw_response: str
    parsed_json: dict[str, Any] | None
    draft: LlmVisualPlanDraft | None
    used_repair: bool = False
    used_fallback: bool = False
    errors: list[str] = field(default_factory=list)
