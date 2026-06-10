"""Style draft builder tests."""

from semantic_visual_builder.image_style.image_metadata import ImageMetadata
from semantic_visual_builder.image_style.image_style_analyzer import (
    DeterministicImageStyleAnalysis,
)
from semantic_visual_builder.image_style.palette_extractor import (
    ExtractedColour,
    PaletteExtractionResult,
)
from semantic_visual_builder.image_style.style_draft_builder import StyleDraftBuilder
from semantic_visual_builder.styles.style_validator import StyleValidator


def test_style_draft_builder_produces_valid_profile() -> None:
    palette = PaletteExtractionResult(
        colours=[
            ExtractedColour("#1f4e79", (31, 78, 121), 65.0),
            ExtractedColour("#5b9bd5", (91, 155, 213), 20.0),
            ExtractedColour("#d9d9d9", (217, 217, 217), 15.0),
        ],
        background_colour="#ffffff",
        primary_colour="#1f4e79",
        accent_colour="#5b9bd5",
        neutral_colour="#d9d9d9",
    )
    analysis = DeterministicImageStyleAnalysis(
        palette=palette,
        background_tone="light",
        contrast_level="high",
        chart_tone="corporate",
        grid_hint="light",
        label_density_hint="medium",
    )
    metadata = ImageMetadata(
        path="sample.png",
        format="PNG",
        width=1280,
        height=720,
        mode="RGB",
        aspect_ratio=16 / 9,
    )

    profile = StyleDraftBuilder().build_style_profile(
        "Extracted Blue Report Style", metadata, palette, analysis
    )

    assert profile.metadata.style_name == "Extracted Blue Report Style"
    assert profile.palette.primary == "#1f4e79"
    assert profile.chart.background == "#ffffff"
    assert profile.chart.grid == "light"
    assert profile.metadata.tags
    assert StyleValidator().validate_style(profile).is_valid is True
