"""Tests for SchemaMatcher."""

from __future__ import annotations


from semantic_visual_builder.data.data_profiler import ColumnProfile, DatasetProfile
from semantic_visual_builder.data.schema_matcher import SchemaMatcher


def _profile(*column_names: str, semantic_types: dict[str, str] | None = None) -> DatasetProfile:
    sem = semantic_types or {}
    cols = [
        ColumnProfile(
            name=name,
            dtype="object",
            semantic_type=sem.get(name),
            null_count=0,
            null_percent=0.0,
            unique_count=5,
            sample_values=[],
        )
        for name in column_names
    ]
    return DatasetProfile(columns=cols, row_count=5, column_count=len(cols))


class TestExactMatch:
    def test_exact_match_score_1(self) -> None:
        profile = _profile("month", "sales")
        report = SchemaMatcher().match_fields(["month", "sales"], profile)
        for m in report.matches:
            assert m.score == 1.0
            assert m.reason == "exact"

    def test_overall_score_1_on_exact(self) -> None:
        profile = _profile("a", "b")
        report = SchemaMatcher().match_fields(["a", "b"], profile)
        assert report.overall_score == 1.0

    def test_no_errors_on_exact(self) -> None:
        profile = _profile("x")
        report = SchemaMatcher().match_fields(["x"], profile)
        assert report.errors == []


class TestCaseInsensitiveMatch:
    def test_case_insensitive(self) -> None:
        profile = _profile("Month")
        report = SchemaMatcher().match_fields(["month"], profile)
        assert report.matches[0].score == 0.95
        assert report.matches[0].target_field == "Month"

    def test_mixed_case(self) -> None:
        profile = _profile("SaleAmount")
        report = SchemaMatcher().match_fields(["saleamount"], profile)
        assert report.matches[0].score == 0.95


class TestNormalizedMatch:
    def test_snake_to_spaces(self) -> None:
        profile = _profile("sale amount")
        report = SchemaMatcher().match_fields(["sale_amount"], profile)
        assert report.matches[0].score == 0.85
        assert report.matches[0].reason == "normalized"

    def test_dashes_normalized(self) -> None:
        profile = _profile("sale-amount")
        report = SchemaMatcher().match_fields(["sale_amount"], profile)
        assert report.matches[0].score == 0.85


class TestAliasMatch:
    def test_alias_match(self) -> None:
        profile = _profile("revenue")
        report = SchemaMatcher().match_fields(
            ["sales"],
            profile,
            aliases={"sales": ["revenue", "income"]},
        )
        assert report.matches[0].score == 0.80
        assert report.matches[0].target_field == "revenue"


class TestSemanticTypeFallback:
    def test_semantic_type_fallback(self) -> None:
        profile = _profile("qty", semantic_types={"qty": "measure"})
        report = SchemaMatcher().match_fields(
            ["amount"],
            profile,
            expected_semantic_types={"amount": "measure"},
        )
        assert report.matches[0].score == 0.50
        assert report.matches[0].reason == "semantic_type_fallback"


class TestNoMatch:
    def test_no_match_adds_error(self) -> None:
        profile = _profile("x")
        report = SchemaMatcher().match_fields(["zzz_unknown"], profile)
        assert report.matches[0].target_field is None
        assert any("zzz_unknown" in e for e in report.errors)

    def test_no_match_score_zero(self) -> None:
        profile = _profile("x")
        report = SchemaMatcher().match_fields(["zzz_unknown"], profile)
        assert report.matches[0].score == 0.0


class TestOverallScore:
    def test_low_match_adds_warning(self) -> None:
        profile = _profile("x")
        report = SchemaMatcher().match_fields(["no_match_a", "no_match_b"], profile)
        assert any("low" in w.lower() for w in report.warnings)

    def test_partial_match_score_between(self) -> None:
        profile = _profile("a", "b")
        report = SchemaMatcher().match_fields(["a", "zzz_missing"], profile)
        assert 0.0 < report.overall_score < 1.0

    def test_used_target_not_reused(self) -> None:
        profile = _profile("value")
        report = SchemaMatcher().match_fields(["field_a", "field_b"], profile, aliases={"field_a": ["value"], "field_b": ["value"]})
        matched = [m for m in report.matches if m.target_field == "value"]
        assert len(matched) == 1
