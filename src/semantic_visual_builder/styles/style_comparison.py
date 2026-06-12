"""Compare style profiles to detect similarity."""

from __future__ import annotations

import math
from dataclasses import dataclass

from .style_schema import StyleProfile


@dataclass
class StyleComparisonResult:
    compared_style_id: str
    compared_style_name: str
    similarity_score: float
    reasons: list[str]

    @property
    def similarity_label(self) -> str:
        if self.similarity_score >= 0.85:
            return "very similar"
        if self.similarity_score >= 0.65:
            return "similar"
        if self.similarity_score >= 0.40:
            return "some overlap"
        return "different"

    @property
    def similarity_percent(self) -> int:
        return round(self.similarity_score * 100)


class StyleComparator:
    def compare(
        self,
        candidate: StyleProfile,
        existing: StyleProfile,
    ) -> StyleComparisonResult:
        score = 0.0
        reasons: list[str] = []

        primary_score = self._colour_score(
            candidate.palette.primary, existing.palette.primary
        )
        score += primary_score * 0.30
        if primary_score >= 0.85:
            reasons.append("similar blue primary" if self._is_blue(candidate.palette.primary) else "similar primary colour")
        elif primary_score <= 0.35:
            reasons.append("different primary colour")

        bg_score = self._background_tone_score(
            candidate.chart.background, existing.chart.background
        )
        score += bg_score * 0.20
        if bg_score >= 0.9:
            reasons.append("similar background tone")
        elif bg_score <= 0.3:
            reasons.append("different background tone")

        accent_score = self._colour_score(
            candidate.palette.accent, existing.palette.accent
        )
        score += accent_score * 0.20
        if accent_score <= 0.4 and (candidate.palette.accent or existing.palette.accent):
            reasons.append("different accent colours")

        grid_match = (candidate.chart.grid or "none") == (existing.chart.grid or "none")
        score += 0.10 if grid_match else 0.0
        if not grid_match:
            reasons.append("different grid style")

        density_match = (candidate.chart.label_density or "medium") == (
            existing.chart.label_density or "medium"
        )
        score += 0.05 if density_match else 0.0

        tag_score = self._tag_overlap_score(candidate.metadata.tags, existing.metadata.tags)
        score += tag_score * 0.15
        if tag_score >= 0.5:
            shared = set(candidate.metadata.tags) & set(existing.metadata.tags)
            reasons.append(f"shared tags: {', '.join(sorted(shared))}")

        return StyleComparisonResult(
            compared_style_id=existing.metadata.style_id,
            compared_style_name=existing.metadata.style_name,
            similarity_score=min(1.0, max(0.0, score)),
            reasons=reasons,
        )

    def rank_similar_styles(
        self,
        candidate: StyleProfile,
        existing_styles: list[StyleProfile],
    ) -> list[StyleComparisonResult]:
        results = [self.compare(candidate, existing) for existing in existing_styles]
        results.sort(key=lambda r: r.similarity_score, reverse=True)
        return results

    def _colour_score(self, hex_a: str | None, hex_b: str | None) -> float:
        if not hex_a and not hex_b:
            return 1.0
        if not hex_a or not hex_b:
            return 0.5
        rgb_a = self._hex_to_rgb(hex_a)
        rgb_b = self._hex_to_rgb(hex_b)
        if rgb_a is None or rgb_b is None:
            return 0.5
        distance = math.sqrt(sum((a - b) ** 2 for a, b in zip(rgb_a, rgb_b, strict=True)))
        max_distance = math.sqrt(3 * 255 ** 2)
        return 1.0 - (distance / max_distance)

    def _background_tone_score(self, hex_a: str | None, hex_b: str | None) -> float:
        tone_a = self._tone(hex_a)
        tone_b = self._tone(hex_b)
        if tone_a == tone_b:
            return 1.0
        if {tone_a, tone_b} == {"light", "neutral"} or {tone_a, tone_b} == {"dark", "neutral"}:
            return 0.6
        return 0.0

    def _tone(self, hex_value: str | None) -> str:
        if not hex_value:
            return "light"
        rgb = self._hex_to_rgb(hex_value)
        if rgb is None:
            return "light"
        brightness = (rgb[0] * 299 + rgb[1] * 587 + rgb[2] * 114) / 1000
        if brightness > 200:
            return "light"
        if brightness < 80:
            return "dark"
        return "neutral"

    def _tag_overlap_score(self, tags_a: list[str], tags_b: list[str]) -> float:
        set_a = set(tags_a)
        set_b = set(tags_b)
        if not set_a and not set_b:
            return 0.5
        if not set_a or not set_b:
            return 0.0
        intersection = len(set_a & set_b)
        union = len(set_a | set_b)
        return intersection / union if union else 0.0

    def _is_blue(self, hex_value: str | None) -> bool:
        if not hex_value:
            return False
        rgb = self._hex_to_rgb(hex_value)
        if rgb is None:
            return False
        return rgb[2] >= rgb[0] and rgb[2] >= rgb[1]

    def _hex_to_rgb(self, hex_value: str) -> tuple[int, int, int] | None:
        text = hex_value.lstrip("#")
        if len(text) == 3:
            text = "".join(c * 2 for c in text)
        if len(text) != 6:
            return None
        return (int(text[0:2], 16), int(text[2:4], 16), int(text[4:6], 16))
