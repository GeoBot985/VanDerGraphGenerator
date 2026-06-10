"""Revision history for accepted visual plans."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field
from datetime import datetime, timezone

from semantic_visual_builder.planning.visual_plan_schema import VisualPlan


@dataclass(frozen=True)
class Revision:
    revision_number: int
    description: str
    visual_plan: VisualPlan
    mapping_method: str | None = None
    timestamp: str | None = None
    preview_stale: bool = True


@dataclass
class RevisionHistory:
    revisions: list[Revision] = field(default_factory=list)

    def add_revision(
        self,
        description: str,
        visual_plan: VisualPlan,
        mapping_method: str | None = None,
        preview_stale: bool = True,
    ) -> Revision:
        revision = Revision(
            revision_number=len(self.revisions) + 1,
            description=description,
            visual_plan=deepcopy(visual_plan),
            mapping_method=mapping_method,
            timestamp=datetime.now(timezone.utc).isoformat(),
            preview_stale=preview_stale,
        )
        self.revisions.append(revision)
        return revision

    def latest(self) -> Revision | None:
        return self.revisions[-1] if self.revisions else None

    def latest_plan(self) -> VisualPlan | None:
        latest = self.latest()
        return deepcopy(latest.visual_plan) if latest else None

    def count(self) -> int:
        return len(self.revisions)
