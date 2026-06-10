"""Recipe compatibility scoring."""

from __future__ import annotations

from dataclasses import dataclass, field
from difflib import SequenceMatcher

from semantic_visual_builder.data.data_profiler import DatasetProfile
from semantic_visual_builder.utils.text_sanitize import normalize_name

from .recipe_schema import RecipeFieldExpectation, VisualRecipe


@dataclass
class FieldMatch:
    expected_field: str
    expected_role: str
    expected_semantic_type: str | None
    matched_field: str | None
    matched_semantic_type: str | None
    score: float
    match_reason: str
    required: bool = True


@dataclass
class RecipeCompatibilityReport:
    recipe_name: str
    overall_score: float
    can_apply: bool
    field_matches: list[FieldMatch] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


class RecipeCompatibilityChecker:
    synonyms = {
        "region": ["province", "area", "location"],
        "amount": ["value", "total", "totalamount"],
        "transactiondate": ["txndate", "date", "transaction_date"],
        "status": ["state", "outcome", "result"],
    }

    def check_compatibility(
        self,
        recipe: VisualRecipe,
        dataset_profile: DatasetProfile,
    ) -> RecipeCompatibilityReport:
        dataset_fields = {
            column.name: column.semantic_type for column in dataset_profile.columns
        }
        matches: list[FieldMatch] = []
        errors: list[str] = []
        warnings: list[str] = []
        required_scores: list[float] = []

        for expected in recipe.expected_fields:
            match = self._match_expected_field(expected, dataset_fields)
            matches.append(match)
            if match.required:
                required_scores.append(match.score)
            if match.score == 0.0 and match.required:
                errors.append(
                    "Missing required field for role "
                    f"'{expected.role}': {expected.field_name}"
                )
            elif match.score < 1.0:
                warnings.append(
                    f"{expected.field_name} matched {match.matched_field or 'nothing'} "
                    f"with score {match.score:.2f} ({match.match_reason})."
                )
            if (
                match.matched_field
                and match.expected_semantic_type
                and match.matched_semantic_type
                and match.expected_semantic_type != match.matched_semantic_type
            ):
                warnings.append(
                    f"Field '{match.matched_field}' is {match.matched_semantic_type} "
                    f"but recipe expected {match.expected_semantic_type}."
                )

        overall_score = (
            sum(required_scores) / len(required_scores) if required_scores else 0.0
        )
        can_apply = not errors and overall_score >= 0.60
        return RecipeCompatibilityReport(
            recipe_name=recipe.recipe_name,
            overall_score=overall_score,
            can_apply=can_apply,
            field_matches=matches,
            errors=errors,
            warnings=warnings,
        )

    def _match_expected_field(
        self, expected: RecipeFieldExpectation, dataset_fields: dict[str, str]
    ) -> FieldMatch:
        candidates = list(dataset_fields.keys())
        if expected.field_name == "row_count":
            return FieldMatch(
                expected_field=expected.field_name,
                expected_role=expected.role,
                expected_semantic_type=expected.semantic_type,
                matched_field="row_count",
                matched_semantic_type="numeric",
                score=1.0,
                match_reason="virtual row count",
                required=expected.required,
            )

        exact = dataset_fields.get(expected.field_name)
        if exact is not None:
            return self._build_match(
                expected, expected.field_name, exact, 1.0, "exact match"
            )

        for candidate in candidates:
            if candidate.lower() == expected.field_name.lower():
                return self._build_match(
                    expected,
                    candidate,
                    dataset_fields[candidate],
                    0.95,
                    "case-insensitive match",
                )

        normalized = normalize_name(expected.field_name)
        for candidate in candidates:
            if normalize_name(candidate) == normalized:
                return self._build_match(
                    expected,
                    candidate,
                    dataset_fields[candidate],
                    0.90,
                    "normalized match",
                )

        expected_normalized = normalize_name(expected.field_name)
        alias_set = {
            normalize_name(alias)
            for alias in expected.aliases
            if isinstance(alias, str)
        }
        for candidate in candidates:
            normalized_candidate = normalize_name(candidate)
            if normalized_candidate in alias_set:
                return self._build_match(
                    expected, candidate, dataset_fields[candidate], 0.85, "alias match"
                )
            for synonym in self.synonyms.get(expected_normalized, []):
                if normalized_candidate == normalize_name(synonym):
                    return self._build_match(
                        expected,
                        candidate,
                        dataset_fields[candidate],
                        0.85,
                        "synonym match",
                    )
                if synonym in self.synonyms.get(normalized_candidate, []):
                    return self._build_match(
                        expected,
                        candidate,
                        dataset_fields[candidate],
                        0.85,
                        "synonym match",
                    )

        best_candidate = None
        best_ratio = 0.0
        for candidate in candidates:
            ratio = SequenceMatcher(
                None, normalize_name(candidate), expected_normalized
            ).ratio()
            if ratio > best_ratio:
                best_ratio = ratio
                best_candidate = candidate
        if best_candidate and best_ratio >= 0.5:
            return self._build_match(
                expected,
                best_candidate,
                dataset_fields[best_candidate],
                0.60,
                "weak name similarity",
            )

        return FieldMatch(
            expected_field=expected.field_name,
            expected_role=expected.role,
            expected_semantic_type=expected.semantic_type,
            matched_field=None,
            matched_semantic_type=None,
            score=0.0,
            match_reason="missing required field"
            if expected.required
            else "optional field missing",
            required=expected.required,
        )

    def _build_match(
        self,
        expected: RecipeFieldExpectation,
        matched_field: str,
        matched_semantic_type: str | None,
        score: float,
        reason: str,
    ) -> FieldMatch:
        if (
            expected.semantic_type
            and matched_semantic_type
            and expected.semantic_type != matched_semantic_type
        ):
            score = min(score, 0.30)
            reason = f"{reason}; semantic type mismatch"
        return FieldMatch(
            expected_field=expected.field_name,
            expected_role=expected.role,
            expected_semantic_type=expected.semantic_type,
            matched_field=matched_field,
            matched_semantic_type=matched_semantic_type,
            score=score,
            match_reason=reason,
            required=expected.required,
        )
