"""Revision history for accepted visual plans."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field

from semantic_visual_builder.planning.visual_plan_schema import VisualPlan


@dataclass(frozen=True)
class Revision:
    revision_number: int
    description: str
    visual_plan: VisualPlan


@dataclass
class RevisionHistory:
    revisions: list[Revision] = field(default_factory=list)

    def add_revision(self, description: str, visual_plan: VisualPlan) -> Revision:
        revision = Revision(
            revision_number=len(self.revisions) + 1,
            description=description,
            visual_plan=deepcopy(visual_plan),
        )
        self.revisions.append(revision)
        return revision

    def latest(self) -> Revision | None:
        return self.revisions[-1] if self.revisions else None

    def count(self) -> int:
        return len(self.revisions)
