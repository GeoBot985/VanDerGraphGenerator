"""Palette extraction tests."""

import re
from pathlib import Path

from PIL import Image, ImageDraw

from semantic_visual_builder.image_style.colour_utils import colour_distance
from semantic_visual_builder.image_style.image_loader import ImageLoader
from semantic_visual_builder.image_style.palette_extractor import PaletteExtractor


def _make_chart_like_image(path: Path) -> None:
    image = Image.new("RGB", (400, 260), "#ffffff")
    draw = ImageDraw.Draw(image)
    draw.rectangle([40, 40, 180, 220], fill="#1f4e79")
    draw.rectangle([200, 80, 340, 220], fill="#70ad47")
    draw.rectangle([40, 230, 340, 245], fill="#d9d9d9")
    image.save(path)


def test_palette_extractor_identifies_dominant_and_background_colours(
    tmp_path: Path,
) -> None:
    path = tmp_path / "chart.png"
    _make_chart_like_image(path)
    loaded = ImageLoader().load(path)

    result = PaletteExtractor().extract_palette(loaded)

    assert result.background_colour == "#ffffff"
    assert result.primary_colour is not None
    assert result.accent_colour is not None
    assert colour_distance(_hex_to_rgb(result.primary_colour), (31, 78, 121)) < 40
    assert re.fullmatch(r"#[0-9a-f]{6}", result.primary_colour.lower())
    assert len(result.colours) <= 8


def test_palette_extractor_handles_dark_background(tmp_path: Path) -> None:
    path = tmp_path / "dark.png"
    image = Image.new("RGB", (200, 200), "#111111")
    ImageDraw.Draw(image).rectangle([40, 40, 160, 160], fill="#2f7d32")
    image.save(path)
    loaded = ImageLoader().load(path)

    result = PaletteExtractor().extract_palette(loaded)

    assert result.background_colour == "#111111"
    assert result.primary_colour is not None
    assert result.neutral_colour is None or result.neutral_colour.startswith("#")


def _hex_to_rgb(hex_value: str) -> tuple[int, int, int]:
    text = hex_value.lstrip("#")
    return tuple(int(text[index : index + 2], 16) for index in (0, 2, 4))
