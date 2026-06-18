"""Deterministic schema field matching for recipes and imports."""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from .data_profiler import ColumnProfile, DatasetProfile


@dataclass
class SchemaFieldMatch:
    source_field: str
    target_field: str | None
    source_semantic_type: str | None
    target_semantic_type: str | None
    score: float
    reason: str


@dataclass
class SchemaMatchReport:
    overall_score: float
    matches: list[SchemaFieldMatch]
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


class SchemaMatcher:
    """Match expected field names against a loaded dataset profile using deterministic rules.

    Priority order:
    1. Exact match
    2. Case-insensitive match
    3. Normalized name match (snake_case / spaces stripped)
    4. Alias/synonym match
    5. Semantic type fallback
    """

    def match_fields(
        self,
        expected_fields: list[str],
        dataset_profile: DatasetProfile,
        expected_semantic_types: dict[str, str] | None = None,
        aliases: dict[str, list[str]] | None = None,
    ) -> SchemaMatchReport:
        available = {col.name: col for col in dataset_profile.columns}
        sem_types = expected_semantic_types or {}
        alias_map = aliases or {}
        matches: list[SchemaFieldMatch] = []
        warnings: list[str] = []
        errors: list[str] = []
        used_targets: set[str] = set()

        for expected in expected_fields:
            target, score, reason = self._find_best_match(
                expected,
                available,
                sem_types.get(expected),
                alias_map.get(expected, []),
                used_targets,
            )
            target_col = available.get(target) if target else None
            matches.append(
                SchemaFieldMatch(
                    source_field=expected,
                    target_field=target,
                    source_semantic_type=sem_types.get(expected),
                    target_semantic_type=target_col.semantic_type if target_col else None,
                    score=score,
                    reason=reason,
                )
            )
            if target:
                used_targets.add(target)
            else:
                errors.append(f"No match found for required field '{expected}'.")

        if matches:
            matched_scores = [m.score for m in matches if m.target_field]
            overall = sum(matched_scores) / len(matches) if matches else 0.0
        else:
            overall = 0.0

        if overall < 0.6:
            warnings.append(
                "Overall schema match is low. Manual field mapping may be required."
            )

        return SchemaMatchReport(
            overall_score=round(overall, 4),
            matches=matches,
            warnings=warnings,
            errors=errors,
        )

    def _find_best_match(
        self,
        expected: str,
        available: dict[str, ColumnProfile],
        expected_semantic_type: str | None,
        field_aliases: list[str],
        used_targets: set[str],
    ) -> tuple[str | None, float, str]:
        candidates = [name for name in available if name not in used_targets]

        # 1. Exact match
        if expected in candidates:
            return expected, 1.0, "exact"

        # 2. Case-insensitive
        for name in candidates:
            if name.lower() == expected.lower():
                return name, 0.95, "case-insensitive"

        # 3. Normalized name (remove spaces, underscores, lowercase)
        expected_norm = self._normalize(expected)
        for name in candidates:
            if self._normalize(name) == expected_norm:
                return name, 0.85, "normalized"

        # 4. Alias match
        alias_norms = [self._normalize(a) for a in field_aliases]
        for name in candidates:
            if self._normalize(name) in alias_norms:
                return name, 0.80, "alias"
            if name.lower() in [a.lower() for a in field_aliases]:
                return name, 0.80, "alias"

        # 5. Semantic type fallback
        if expected_semantic_type:
            for name in candidates:
                col = available.get(name)
                if hasattr(col, "semantic_type") and col.semantic_type == expected_semantic_type:  # type: ignore[union-attr]
                    return name, 0.50, "semantic_type_fallback"

        return None, 0.0, "no_match"

    def _normalize(self, name: str) -> str:
        return re.sub(r"[\s_\-]+", "", name).lower()
