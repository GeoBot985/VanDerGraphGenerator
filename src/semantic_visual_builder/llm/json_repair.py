"""Repair prompt helpers for invalid LLM JSON."""

from __future__ import annotations

from .prompts import VISUAL_REPAIR_SYSTEM_PROMPT


class JsonRepair:
    """Build a repair prompt for a malformed JSON response."""

    def build_repair_prompt(self, invalid_response: str, error: str) -> str:
        return (
            f"{VISUAL_REPAIR_SYSTEM_PROMPT}\n\n"
            "The following response was invalid.\n"
            f"Parser error: {error}\n\n"
            "Invalid response:\n"
            f"{invalid_response}\n\n"
            "Return one valid JSON object only."
        )
