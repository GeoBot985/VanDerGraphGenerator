"""Style review dialog model — logic layer for reviewing extracted styles before saving."""

from __future__ import annotations

from dataclasses import dataclass

from semantic_visual_builder.styles.style_review_model import (
    EditableStyleDraft,
    style_profile_from_editable_draft,
    validate_editable_draft,
)
from semantic_visual_builder.styles.style_schema import StyleProfile

_ALLOWED_GRID = ("none", "light", "medium")
_ALLOWED_DENSITY = ("low", "medium", "high")


@dataclass
class StyleReviewDialogResult:
    action: str
    style_profile: StyleProfile | None
    errors: list[str]


class StyleReviewDialogController:
    """Logic controller for the style review dialog.

    The actual Tkinter dialog is not created here so that unit tests can exercise
    the logic without a running display. The Tkinter layer calls these methods.
    """

    def __init__(self, draft: EditableStyleDraft) -> None:
        self._draft = draft

    @property
    def draft(self) -> EditableStyleDraft:
        return self._draft

    def update_field(self, field_name: str, value: str) -> None:
        """Update a single field on the draft."""
        if hasattr(self._draft, field_name):
            setattr(self._draft, field_name, value or None)

    def get_display_lines(self) -> list[str]:
        """Return lines describing the current draft for display."""
        draft = self._draft
        lines = [
            f"Name: {draft.style_name or '(unnamed)'}",
            f"Description: {draft.description or ''}",
            "",
            "Palette:",
            f"  Primary:    {draft.primary or '(none)'}",
            f"  Secondary:  {draft.secondary or '(none)'}",
            f"  Accent:     {draft.accent or '(none)'}",
            f"  Neutral:    {draft.neutral or '(none)'}",
            f"  Background: {draft.background or '(none)'}",
            f"  Plot bg:    {draft.plot_background or '(none)'}",
            f"  Text:       {draft.text_colour or '(auto)'}",
            "",
            "Chart:",
            f"  Grid:           {draft.grid or '(none)'}",
            f"  Label density:  {draft.label_density or '(none)'}",
            f"  Tone:           {draft.chart_tone or '(none)'}",
            "",
            f"Tags: {', '.join(draft.tags) if draft.tags else '(none)'}",
        ]
        if draft.warnings:
            lines.append("")
            lines.append("Warnings:")
            lines.extend(f"  - {w}" for w in draft.warnings)
        return lines

    def validate(self) -> list[str]:
        """Return list of validation errors for the current draft."""
        errors = validate_editable_draft(self._draft)
        additional: list[str] = []
        if self._draft.grid and self._draft.grid not in _ALLOWED_GRID:
            additional.append(
                f"Grid must be one of: {', '.join(_ALLOWED_GRID)}. Got: {self._draft.grid}"
            )
        if self._draft.label_density and self._draft.label_density not in _ALLOWED_DENSITY:
            additional.append(
                f"Label density must be one of: {', '.join(_ALLOWED_DENSITY)}. Got: {self._draft.label_density}"
            )
        return errors + additional

    def save(self) -> StyleReviewDialogResult:
        """Attempt to build and validate the StyleProfile from the draft.

        Returns action='save' with the profile on success, or action='invalid' with errors.
        """
        errors = self.validate()
        if errors:
            return StyleReviewDialogResult(action="invalid", style_profile=None, errors=errors)
        profile = style_profile_from_editable_draft(self._draft)
        return StyleReviewDialogResult(action="save", style_profile=profile, errors=[])

    def apply_without_saving(self) -> StyleReviewDialogResult:
        """Build profile for immediate application without persisting."""
        errors = self.validate()
        if errors:
            return StyleReviewDialogResult(action="invalid", style_profile=None, errors=errors)
        profile = style_profile_from_editable_draft(self._draft)
        return StyleReviewDialogResult(action="apply", style_profile=profile, errors=[])

    def cancel(self) -> StyleReviewDialogResult:
        return StyleReviewDialogResult(action="cancel", style_profile=None, errors=[])
