"""Image style analyzer tests."""

from pathlib import Path

from PIL import Image

from semantic_visual_builder.image_style.image_loader import ImageLoader
from semantic_visual_builder.image_style.image_style_analyzer import ImageStyleAnalyzer
from semantic_visual_builder.image_style.palette_extractor import (
    ExtractedColour,
    PaletteExtractionResult,
)


def test_analyzer_detects_light_corporate_tone(tmp_path: Path) -> None:
    path = tmp_path / "light.png"
    Image.new("RGB", (320, 240), "#ffffff").save(path)
    loaded = ImageLoader().load(path)
    palette = PaletteExtractionResult(
        colours=[
            ExtractedColour("#1f4e79", (31, 78, 121), 60.0),
            ExtractedColour("#5b9bd5", (91, 155, 213), 20.0),
            ExtractedColour("#d9d9d9", (217, 217, 217), 20.0),
        ],
        background_colour="#ffffff",
        primary_colour="#1f4e79",
        accent_colour="#5b9bd5",
        neutral_colour="#d9d9d9",
    )

    result = ImageStyleAnalyzer().analyze(loaded, palette)

    assert result.background_tone == "light"
    assert result.chart_tone == "corporate"
    assert result.grid_hint == "light"
    assert result.label_density_hint == "medium"


def test_analyzer_detects_dark_presentation_tone(tmp_path: Path) -> None:
    path = tmp_path / "dark.png"
    Image.new("RGB", (320, 240), "#111111").save(path)
    loaded = ImageLoader().load(path)
    palette = PaletteExtractionResult(
        colours=[
            ExtractedColour("#e53935", (229, 57, 53), 60.0),
            ExtractedColour("#ffb300", (255, 179, 0), 20.0),
        ],
        background_colour="#111111",
        primary_colour="#e53935",
        accent_colour="#ffb300",
    )

    result = ImageStyleAnalyzer().analyze(loaded, palette)

    assert result.background_tone == "dark"
    assert result.chart_tone == "presentation"
    assert result.grid_hint == "none"
