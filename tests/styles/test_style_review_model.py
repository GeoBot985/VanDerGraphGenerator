"""Tests for EditableStyleDraft and conversion helpers."""

from __future__ import annotations

from semantic_visual_builder.styles.style_review_model import (
    EditableStyleDraft,
    editable_draft_from_style_profile,
    style_profile_from_editable_draft,
    validate_editable_draft,
)
from semantic_visual_builder.styles.style_schema import (
    ChartStyle,
    ColourPalette,
    StyleMetadata,
    StyleProfile,
)


def _make_profile(
    style_id: str = "test_style",
    primary: str = "#1f4e79",
    background: str = "#ffffff",
    tags: list[str] | None = None,
) -> StyleProfile:
    return StyleProfile(
        metadata=StyleMetadata(
            style_id=style_id,
            style_name="Test Style",
            tags=tags or ["corporate", "light"],
        ),
        palette=ColourPalette(
            primary=primary,
            secondary="#5b9bd5",
            accent="#70ad47",
            neutral="#a5a5a5",
        ),
        chart=ChartStyle(
            background=background,
            grid="light",
            label_density="medium",
        ),
    )


class TestEditableDraftFromProfile:
    def test_basic_fields_populated(self) -> None:
        profile = _make_profile()
        draft = editable_draft_from_style_profile(profile)
        assert draft.style_id == "test_style"
        assert draft.style_name == "Test Style"
        assert draft.primary == "#1f4e79"
        assert draft.secondary == "#5b9bd5"
        assert draft.accent == "#70ad47"
        assert draft.background == "#ffffff"
        assert draft.grid == "light"
        assert draft.label_density == "medium"

    def test_tags_preserved(self) -> None:
        profile = _make_profile(tags=["corporate", "light", "report"])
        draft = editable_draft_from_style_profile(profile)
        assert "corporate" in draft.tags

    def test_warnings_empty_initially(self) -> None:
        draft = editable_draft_from_style_profile(_make_profile())
        assert draft.warnings == []


class TestStyleProfileFromDraft:
    def test_roundtrip_produces_valid_profile(self) -> None:
        profile = _make_profile()
        draft = editable_draft_from_style_profile(profile)
        restored = style_profile_from_editable_draft(draft)
        assert restored.style_id == profile.style_id
        assert restored.style_name == profile.style_name
        assert restored.palette.primary == profile.palette.primary

    def test_edited_accent_reflected(self) -> None:
        profile = _make_profile()
        draft = editable_draft_from_style_profile(profile)
        draft.accent = "#ffc000"
        restored = style_profile_from_editable_draft(draft)
        assert restored.palette.accent == "#ffc000"

    def test_tags_include_chart_tone(self) -> None:
        draft = EditableStyleDraft(
            style_id="s",
            style_name="S",
            chart_tone="corporate",
            tags=[],
        )
        profile = style_profile_from_editable_draft(draft)
        assert "corporate" in profile.metadata.tags

    def test_dark_background_sets_plotly_dark_template(self) -> None:
        draft = EditableStyleDraft(
            style_id="dark",
            style_name="Dark",
            background="#111111",
            tags=[],
        )
        profile = style_profile_from_editable_draft(draft)
        assert profile.renderer_hints.plotly_template == "plotly_dark"


class TestValidateEditableDraft:
    def test_valid_draft_has_no_errors(self) -> None:
        draft = EditableStyleDraft(
            style_id="valid_style",
            style_name="Valid Style",
            primary="#1f4e79",
            background="#ffffff",
            grid="light",
            label_density="medium",
            tags=[],
        )
        errors = validate_editable_draft(draft)
        assert errors == []

    def test_invalid_hex_produces_error(self) -> None:
        draft = EditableStyleDraft(
            style_id="bad",
            style_name="Bad",
            primary="#zzzzzz",
            tags=[],
        )
        errors = validate_editable_draft(draft)
        assert any("colour" in e.lower() or "invalid" in e.lower() for e in errors)
