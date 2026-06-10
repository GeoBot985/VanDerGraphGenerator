"""Clarification request models."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class ClarificationOption:
    label: str
    value: str


@dataclass
class ClarificationRequest:
    question: str
    reason: str
    field_name: str | None = None
    options: list[ClarificationOption] = field(default_factory=list)
    required: bool = True


@dataclass
class PendingClarification:
    request: ClarificationRequest
    partial_plan_json: dict | None = None
    partial_plan_id: str | None = None
