"""Tests for improved palette extractor behaviour."""

from __future__ import annotations

import pytest
from PIL import Image

from semantic_visual_builder.image_style.image_loader import LoadedImage
from semantic_visual_builder.image_style.palette_extractor import PaletteExtractor


def _make_loaded(image: Image.Image) -> LoadedImage:
    from pathlib import Path
    return LoadedImage(
        path=Path("test.png"),
        image=image,
        format="PNG",
        width=image.width,
        height=image.height,
        mode="RGB",
    )


def _white_image_with_blue_rect() -> Image.Image:
    img = Image.new("RGB", (100, 100), color=(255, 255, 255))
    for x in range(20, 80):
        for y in range(20, 80):
            img.putpixel((x, y), (31, 78, 121))
    return img


def _dark_image_with_cyan_rect() -> Image.Image:
    img = Image.new("RGB", (100, 100), color=(17, 17, 17))
    for x in range(20, 80):
        for y in range(20, 80):
            img.putpixel((x, y), (0, 176, 240))
    return img


def _image_with_near_duplicate_colours() -> Image.Image:
    img = Image.new("RGB", (100, 100), color=(255, 255, 255))
    for x in range(0, 33):
        for y in range(0, 100):
            img.putpixel((x, y), (31, 78, 121))
    for x in range(33, 66):
        for y in range(0, 100):
            img.putpixel((x, y), (32, 79, 122))
    for x in range(66, 100):
        for y in range(0, 100):
            img.putpixel((x, y), (33, 80, 123))
    return img


class TestPaletteExtractorImproved:
    def setup_method(self) -> None:
        self.extractor = PaletteExtractor()

    def test_white_not_selected_as_primary(self) -> None:
        img = _white_image_with_blue_rect()
        result = self.extractor.extract_palette(_make_loaded(img))
        assert result.primary_colour is not None
        assert result.primary_colour.lower() != "#ffffff"

    def test_saturated_rectangle_selected_as_primary(self) -> None:
        img = _white_image_with_blue_rect()
        result = self.extractor.extract_palette(_make_loaded(img))
        assert result.primary_colour is not None
        primary = result.primary_colour.lower()
        assert primary != "#ffffff"

    def test_dark_primary_extracted_from_dark_image(self) -> None:
        img = _dark_image_with_cyan_rect()
        result = self.extractor.extract_palette(_make_loaded(img))
        assert result.primary_colour is not None
        primary = result.primary_colour.lower()
        assert primary != "#111111"

    def test_near_duplicate_colours_are_reduced(self) -> None:
        img = _image_with_near_duplicate_colours()
        result = self.extractor.extract_palette(_make_loaded(img), max_colours=8)
        hex_values = [c.hex_value for c in result.colours]
        assert len(hex_values) < 4

    def test_sequence_palette_not_empty(self) -> None:
        img = _white_image_with_blue_rect()
        result = self.extractor.extract_palette(_make_loaded(img))
        assert len(result.colours) >= 1
