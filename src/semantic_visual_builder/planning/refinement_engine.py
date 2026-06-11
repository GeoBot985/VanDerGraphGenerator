"""Legacy compatibility wrapper for structured refinement patching."""

from __future__ import annotations

from .deterministic_fallback_patch_planner import DeterministicFallbackPatchPlanner
from .visual_plan_patch_applier import VisualPlanPatchApplier
from .visual_plan_schema import VisualPlan


class RefinementEngine:
    """Compatibility adapter that applies a deterministic fallback patch."""

    def __init__(self) -> None:
        self._planner = DeterministicFallbackPatchPlanner()
        self._applier = VisualPlanPatchApplier()

    def apply_refinement(self, current_plan: VisualPlan, message: str) -> VisualPlan:
        patch = self._planner.build_patch(current_plan, message)
        return self._applier.apply_patch(current_plan, patch)
