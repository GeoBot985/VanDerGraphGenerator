"""Tests for StyleComparator and StyleComparisonResult."""

from __future__ import annotations

from semantic_visual_builder.styles.style_comparison import StyleComparator
from semantic_visual_builder.styles.style_schema import (
    ChartStyle,
    ColourPalette,
    StyleMetadata,
    StyleProfile,
)


def _make_profile(
    style_id: str = "s",
    style_name: str = "S",
    primary: str | None = None,
    accent: str | None = None,
    background: str | None = None,
    grid: str | None = None,
    label_density: str | None = None,
    tags: list[str] | None = None,
) -> StyleProfile:
    return StyleProfile(
        metadata=StyleMetadata(
            style_id=style_id,
            style_name=style_name,
            tags=tags or [],
        ),
        palette=ColourPalette(primary=primary, accent=accent),
        chart=ChartStyle(background=background, grid=grid, label_density=label_density),
    )


class TestStyleComparator:
    def setup_method(self) -> None:
        self.comparator = StyleComparator()

    def test_identical_styles_score_high(self) -> None:
        profile = _make_profile(
            style_id="a",
            primary="#1f4e79",
            background="#ffffff",
            grid="light",
            label_density="medium",
            tags=["corporate"],
        )
        result = self.comparator.compare(profile, profile)
        assert result.similarity_score >= 0.85

    def test_different_primary_reduces_score(self) -> None:
        a = _make_profile(style_id="a", primary="#1f4e79", background="#ffffff")
        b = _make_profile(style_id="b", primary="#ff0000", background="#ffffff")
        result = self.comparator.compare(a, b)
        assert result.similarity_score < 0.85

    def test_different_background_tone_reduces_score(self) -> None:
        light = _make_profile(style_id="a", background="#ffffff")
        dark = _make_profile(style_id="b", background="#111111")
        result = self.comparator.compare(light, dark)
        assert result.similarity_score < 0.85

    def test_same_background_tone_contributes_positively(self) -> None:
        a = _make_profile(style_id="a", background="#ffffff")
        b = _make_profile(style_id="b", background="#f5f5f5")
        result = self.comparator.compare(a, b)
        assert result.similarity_score > 0.5

    def test_shared_tags_increase_score(self) -> None:
        a = _make_profile(style_id="a", tags=["corporate", "light"])
        b_no_tags = _make_profile(style_id="b", tags=[])
        b_with_tags = _make_profile(style_id="c", tags=["corporate", "light"])
        result_no = self.comparator.compare(a, b_no_tags)
        result_yes = self.comparator.compare(a, b_with_tags)
        assert result_yes.similarity_score > result_no.similarity_score

    def test_rank_returns_highest_similarity_first(self) -> None:
        candidate = _make_profile(
            style_id="c", primary="#1f4e79", background="#ffffff", tags=["corporate"]
        )
        similar = _make_profile(
            style_id="similar", primary="#1a4070", background="#ffffff", tags=["corporate"]
        )
        different = _make_profile(
            style_id="different", primary="#ff0000", background="#111111"
        )
        ranked = self.comparator.rank_similar_styles(candidate, [different, similar])
        assert ranked[0].compared_style_id == "similar"

    def test_score_bounded_0_to_1(self) -> None:
        a = _make_profile(style_id="a", primary="#000000")
        b = _make_profile(style_id="b", primary="#ffffff")
        result = self.comparator.compare(a, b)
        assert 0.0 <= result.similarity_score <= 1.0

    def test_similarity_label_very_similar(self) -> None:
        profile = _make_profile(style_id="a", background="#ffffff", grid="light", tags=["x"])
        result = self.comparator.compare(profile, profile)
        assert result.similarity_label == "very similar"

    def test_similarity_label_different(self) -> None:
        a = _make_profile(style_id="a", primary="#ff0000", background="#111111")
        b = _make_profile(style_id="b", primary="#00ff00", background="#ffffff", tags=["other"])
        result = self.comparator.compare(a, b)
        assert result.similarity_label in ("different", "some overlap", "similar")

    def test_reasons_populated(self) -> None:
        a = _make_profile(style_id="a", primary="#1f4e79", background="#ffffff", tags=["corporate"])
        b = _make_profile(style_id="b", primary="#1f4e79", background="#ffffff", tags=["corporate"])
        result = self.comparator.compare(a, b)
        assert isinstance(result.reasons, list)
