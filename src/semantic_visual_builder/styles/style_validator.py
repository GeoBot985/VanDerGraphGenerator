"""Validate style profiles."""

from __future__ import annotations

import re
from typing import Any

from semantic_visual_builder.validation.validation_result import ValidationResult

from .style_schema import StyleProfile


class StyleValidator:
    allowed_visual_kinds = {"chart", "diagram"}
    allowed_renderers = {"plotly", "chartjs", "mermaid"}
    allowed_grid = {"none", "light", "medium"}
    allowed_label_density = {"low", "medium", "high"}
    allowed_legend_position = {"right", "bottom", "none"}
    allowed_direction = {"TD", "LR", "BT", "RL"}
    _hex_colour = re.compile(r"^#(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{6})$")
    _font_family = re.compile(r"^[A-Za-z0-9 ,\-']+$")
    _blocked_strings = ("javascript:", "url(", "expression(", "<script", "{", "}")

    def validate_style(self, style: StyleProfile) -> ValidationResult:
        result = ValidationResult()
        metadata = style.metadata
        if not metadata.style_id.strip():
            result.add_error("metadata.style_id must not be blank.")
        if not metadata.style_name.strip():
            result.add_error("metadata.style_name must not be blank.")
        if not metadata.schema_version.strip():
            result.add_error("metadata.schema_version must not be blank.")
        if metadata.schema_version != "1.0":
            result.add_error("Style schema_version must be 1.0.")
        if not style.supported_visual_kinds:
            result.add_error("supported_visual_kinds must not be empty.")
        if not style.supported_renderers:
            result.add_error("supported_renderers must not be empty.")
        for item in style.supported_visual_kinds:
            if item not in self.allowed_visual_kinds:
                result.add_error(f"Unsupported visual kind: {item}")
        for item in style.supported_renderers:
            if item not in self.allowed_renderers:
                result.add_error(f"Unsupported renderer: {item}")
        if style.chart.grid and style.chart.grid not in self.allowed_grid:
            result.add_error(f"Unsupported chart grid: {style.chart.grid}")
        if style.chart.label_density and style.chart.label_density not in self.allowed_label_density:
            result.add_error(f"Unsupported label density: {style.chart.label_density}")
        if style.chart.legend_position and style.chart.legend_position not in self.allowed_legend_position:
            result.add_error(f"Unsupported legend position: {style.chart.legend_position}")
        if style.diagram.direction and style.diagram.direction not in self.allowed_direction:
            result.add_error(f"Unsupported diagram direction: {style.diagram.direction}")
        self._validate_colour_values(style.to_dict(), result)
        self._validate_font(style.typography.font_family, result)
        return result

    def validate_style_dict(self, raw: dict[str, Any]) -> ValidationResult:
        try:
            return self.validate_style(StyleProfile.from_dict(raw))
        except Exception as exc:
            result = ValidationResult()
            result.add_error(str(exc))
            return result

    def _validate_colour_values(self, value: Any, result: ValidationResult) -> None:
        if isinstance(value, dict):
            for item in value.values():
                self._validate_colour_values(item, result)
            return
        if isinstance(value, list):
            for item in value:
                self._validate_colour_values(item, result)
            return
        if not isinstance(value, str):
            return
        text = value.strip()
        lowered = text.lower()
        if any(blocked in lowered for blocked in self._blocked_strings):
            result.add_error(f"Unsafe style value: {value}")
            return
        if lowered.startswith("#") and not self._hex_colour.fullmatch(text):
            result.add_error(f"Invalid colour value: {value}")
        elif lowered.startswith("#"):
            return

    def _validate_font(self, font: str | None, result: ValidationResult) -> None:
        if font is None:
            return
        lowered = font.lower()
        if any(blocked in lowered for blocked in self._blocked_strings):
            result.add_error(f"Unsafe font family: {font}")
            return
        if "/" in font or "\\" in font or ":" in font or not self._font_family.fullmatch(font):
            result.add_error(f"Invalid font family: {font}")
