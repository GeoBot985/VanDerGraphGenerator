"""Tests for StyleReviewDialogController logic layer."""

from __future__ import annotations


from semantic_visual_builder.styles.style_review_model import EditableStyleDraft
from semantic_visual_builder.ui.style_review_dialog import StyleReviewDialogController


def _make_draft(**kwargs) -> EditableStyleDraft:
    defaults = {
        "style_id": "test",
        "style_name": "Test Style",
        "primary": "#1f4e79",
        "background": "#ffffff",
        "grid": "light",
        "label_density": "medium",
        "tags": [],
    }
    defaults.update(kwargs)
    return EditableStyleDraft(**defaults)


class TestStyleReviewDialogController:
    def test_display_lines_contain_style_name(self) -> None:
        ctrl = StyleReviewDialogController(_make_draft(style_name="My Style"))
        lines = ctrl.get_display_lines()
        assert any("My Style" in line for line in lines)

    def test_display_lines_contain_primary_colour(self) -> None:
        ctrl = StyleReviewDialogController(_make_draft(primary="#1f4e79"))
        lines = ctrl.get_display_lines()
        assert any("#1f4e79" in line for line in lines)

    def test_update_field_changes_draft(self) -> None:
        ctrl = StyleReviewDialogController(_make_draft(accent="#70ad47"))
        ctrl.update_field("accent", "#ffc000")
        assert ctrl.draft.accent == "#ffc000"

    def test_save_returns_action_save_on_valid_draft(self) -> None:
        ctrl = StyleReviewDialogController(_make_draft())
        result = ctrl.save()
        assert result.action == "save"
        assert result.style_profile is not None
        assert result.errors == []

    def test_save_returns_invalid_on_bad_colour(self) -> None:
        ctrl = StyleReviewDialogController(_make_draft(primary="#zzzzzz"))
        result = ctrl.save()
        assert result.action == "invalid"
        assert result.errors

    def test_apply_without_saving_returns_apply_action(self) -> None:
        ctrl = StyleReviewDialogController(_make_draft())
        result = ctrl.apply_without_saving()
        assert result.action == "apply"
        assert result.style_profile is not None

    def test_cancel_returns_cancel_action(self) -> None:
        ctrl = StyleReviewDialogController(_make_draft())
        result = ctrl.cancel()
        assert result.action == "cancel"
        assert result.style_profile is None

    def test_validate_catches_invalid_grid(self) -> None:
        ctrl = StyleReviewDialogController(_make_draft(grid="invalid_grid"))
        errors = ctrl.validate()
        assert any("grid" in e.lower() for e in errors)

    def test_validate_catches_invalid_density(self) -> None:
        ctrl = StyleReviewDialogController(_make_draft(label_density="ultra"))
        errors = ctrl.validate()
        assert any("density" in e.lower() for e in errors)

    def test_save_edits_are_reflected_in_profile(self) -> None:
        ctrl = StyleReviewDialogController(_make_draft())
        ctrl.update_field("style_name", "Renamed Style")
        result = ctrl.save()
        assert result.style_profile is not None
        assert result.style_profile.style_name == "Renamed Style"
