"""Coordinate style storage and validation."""

from __future__ import annotations

from pathlib import Path

from semantic_visual_builder.validation.validation_result import ValidationResult

from .style_schema import StyleProfile
from .style_store import StyleStore
from .style_validator import StyleValidator


class StyleManager:
    def __init__(
        self,
        style_store: StyleStore,
        style_validator: StyleValidator,
    ):
        self.style_store = style_store
        self.style_validator = style_validator

    def list_styles(self) -> list[StyleProfile]:
        styles = [
            self.style_store.load_style(path)
            for path in self.style_store.list_builtin_styles()
        ]
        styles.extend(
            self.style_store.load_style(path)
            for path in self.style_store.list_user_styles()
        )
        return styles

    def get_style_by_id(self, style_id: str) -> StyleProfile | None:
        for style in self.list_styles():
            if style.style_id == style_id:
                return style
        return None

    def save_style(self, style: StyleProfile) -> Path:
        validation = self.style_validator.validate_style(style)
        if not validation.is_valid:
            errors = "; ".join(message.message for message in validation.messages)
            raise ValueError(errors)
        return self.style_store.save_user_style(style)

    def validate_style(self, style: StyleProfile) -> ValidationResult:
        return self.style_validator.validate_style(style)
