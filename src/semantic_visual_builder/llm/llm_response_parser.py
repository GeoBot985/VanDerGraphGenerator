"""Parse strict JSON responses from the LLM."""

from __future__ import annotations

import json
import re
from typing import Any


class LlmResponseParser:
    """Parse raw or fenced JSON text."""

    def parse_json_response(self, raw_response: str) -> dict[str, Any]:
        text = raw_response.strip()
        if text.startswith("```"):
            text = self._extract_fenced_json(text)
        try:
            data = json.loads(text)
        except json.JSONDecodeError as exc:
            raise ValueError("LLM response is not valid JSON.") from exc
        if not isinstance(data, dict):
            raise ValueError("LLM response must be a single JSON object.")
        return data

    def _extract_fenced_json(self, text: str) -> str:
        pattern = re.compile(r"```(?:json)?\s*(\{.*\})\s*```", re.IGNORECASE | re.DOTALL)
        match = pattern.fullmatch(text)
        if not match:
            raise ValueError("LLM response is not valid fenced JSON.")
        candidate = match.group(1).strip()
        if candidate.count("{") != candidate.count("}") or candidate.count("}") == 0:
            raise ValueError("LLM response is not valid JSON.")
        return candidate
