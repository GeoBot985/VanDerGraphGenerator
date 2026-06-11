"""Legacy compatibility wrapper for the fallback planner."""

from __future__ import annotations

from .deterministic_fallback_mapper import DeterministicFallbackMapper


class IntentMapper(DeterministicFallbackMapper):
    """Compatibility alias for the renamed deterministic fallback mapper."""
