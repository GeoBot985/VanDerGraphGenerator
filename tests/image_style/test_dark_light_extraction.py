"""Tests for dark/light background tone and text colour hint extraction."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from semantic_visual_builder.image_style.image_style_analyzer import ImageStyleAnalyzer
from semantic_visual_builder.image_style.image_loader import LoadedImage
from semantic_visual_builder.image_style.palette_extractor import (
    ExtractedColour,
    PaletteExtractionResult,
)


def _make_loaded_image(width: int = 400, height: int = 300) -> LoadedImage:
    from pathlib import Path
    mock_image = MagicMock()
    return LoadedImage(
        path=Path("test.png"),
        image=mock_image,
        format="PNG",
        width=width,
        height=height,
        mode="RGB",
    )


def _make_palette(bg: tuple[int, int, int], primary: tuple[int, int, int]) -> PaletteExtractionResult:
    def to_hex(rgb: tuple[int, int, int]) -> str:
        return "#{:02x}{:02x}{:02x}".format(*rgb)

    return PaletteExtractionResult(
        colours=[ExtractedColour(hex_value=to_hex(primary), rgb=primary, percentage=50.0)],
        background_colour=to_hex(bg),
        primary_colour=to_hex(primary),
        accent_colour=None,
        neutral_colour=None,
        warnings=[],
    )


class TestDarkLightExtraction:
    def setup_method(self) -> None:
        self.analyzer = ImageStyleAnalyzer()

    def test_dark_background_produces_dark_tone(self) -> None:
        palette = _make_palette(bg=(10, 10, 10), primary=(0, 176, 240))
        result = self.analyzer.analyze(_make_loaded_image(), palette)
        assert result.background_tone == "dark"

    def test_dark_background_text_hint_is_white(self) -> None:
        palette = _make_palette(bg=(10, 10, 10), primary=(0, 176, 240))
        result = self.analyzer.analyze(_make_loaded_image(), palette)
        assert result.text_colour_hint == "#ffffff"

    def test_light_background_produces_light_tone(self) -> None:
        palette = _make_palette(bg=(245, 245, 245), primary=(31, 78, 121))
        result = self.analyzer.analyze(_make_loaded_image(), palette)
        assert result.background_tone == "light"

    def test_light_background_text_hint_is_black(self) -> None:
        palette = _make_palette(bg=(245, 245, 245), primary=(31, 78, 121))
        result = self.analyzer.analyze(_make_loaded_image(), palette)
        assert result.text_colour_hint == "#000000"

    def test_neutral_background_produces_neutral_tone(self) -> None:
        palette = _make_palette(bg=(128, 128, 128), primary=(50, 50, 150))
        result = self.analyzer.analyze(_make_loaded_image(), palette)
        assert result.background_tone == "neutral"

    def test_text_colour_hint_is_readable_for_neutral(self) -> None:
        palette = _make_palette(bg=(128, 128, 128), primary=(50, 50, 150))
        result = self.analyzer.analyze(_make_loaded_image(), palette)
        assert result.text_colour_hint in ("#ffffff", "#000000")

    def test_bg_brightness_threshold_200_is_light(self) -> None:
        palette = _make_palette(bg=(201, 201, 201), primary=(50, 50, 150))
        result = self.analyzer.analyze(_make_loaded_image(), palette)
        assert result.background_tone == "light"

    def test_bg_brightness_threshold_80_is_dark(self) -> None:
        palette = _make_palette(bg=(79, 0, 0), primary=(200, 50, 50))
        result = self.analyzer.analyze(_make_loaded_image(), palette)
        assert result.background_tone == "dark"
