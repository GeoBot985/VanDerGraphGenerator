"""Deterministic recipe field mapping."""

from __future__ import annotations

from difflib import SequenceMatcher

from semantic_visual_builder.data.data_profiler import DatasetProfile
from semantic_visual_builder.utils.text_sanitize import normalize_name

from .recipe_compatibility import RecipeCompatibilityChecker
from .recipe_schema import VisualRecipe


class RecipeFieldMapper:
    def __init__(self) -> None:
        self.compatibility_checker = RecipeCompatibilityChecker()

    def propose_mappings(
        self,
        recipe: VisualRecipe,
        dataset_profile: DatasetProfile,
    ) -> dict[str, str]:
        dataset_fields = {
            column.name: column.semantic_type for column in dataset_profile.columns
        }
        mappings: dict[str, str] = {}
        used_fields: set[str] = set()
        for expected in recipe.expected_fields:
            matched = self._match_field(
                expected.field_name, expected.aliases, dataset_fields, used_fields
            )
            if matched is not None:
                mappings[expected.field_name] = matched
                used_fields.add(matched)
        return mappings

    def _match_field(
        self,
        expected_name: str,
        aliases: list[str],
        dataset_fields: dict[str, str],
        used_fields: set[str],
    ) -> str | None:
        if expected_name == "row_count":
            return "row_count"

        candidates = [name for name in dataset_fields if name not in used_fields]
        if expected_name in candidates:
            return expected_name
        for candidate in candidates:
            if candidate.lower() == expected_name.lower():
                return candidate
        normalized = normalize_name(expected_name)
        for candidate in candidates:
            if normalize_name(candidate) == normalized:
                return candidate

        normalized_aliases = {normalize_name(alias) for alias in aliases if alias}
        for candidate in candidates:
            normalized_candidate = normalize_name(candidate)
            if normalized_candidate in normalized_aliases:
                return candidate
        for candidate in candidates:
            candidate_norm = normalize_name(candidate)
            if any(
                candidate_norm == normalize_name(item)
                for item in self.compatibility_checker.synonyms.get(normalized, [])
            ):
                return candidate
            if any(
                normalize_name(item) == normalized
                for item in self.compatibility_checker.synonyms.get(candidate_norm, [])
            ):
                return candidate

        best_candidate = None
        best_ratio = 0.0
        for candidate in candidates:
            ratio = SequenceMatcher(None, normalize_name(candidate), normalized).ratio()
            if ratio > best_ratio:
                best_ratio = ratio
                best_candidate = candidate
        return best_candidate if best_ratio >= 0.5 else None
