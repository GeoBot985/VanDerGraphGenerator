"""Style extraction panel tests."""

from semantic_visual_builder.image_style.image_metadata import ImageMetadata
from semantic_visual_builder.image_style.image_style_analyzer import (
    DeterministicImageStyleAnalysis,
)
from semantic_visual_builder.image_style.palette_extractor import (
    ExtractedColour,
    PaletteExtractionResult,
)
from semantic_visual_builder.image_style.style_extraction_result import (
    StyleExtractionResult,
)
from semantic_visual_builder.state.app_state import AppState
from semantic_visual_builder.styles.style_schema import (
    ChartStyle,
    ColourPalette,
    StyleMetadata,
    StyleProfile,
)
from semantic_visual_builder.ui.style_extraction_panel import StyleExtractionPanel


def test_style_extraction_panel_formats_summary() -> None:
    state = AppState()
    state.set_selected_style_image_path(None)
    state.set_style_extraction_result(
        StyleExtractionResult(
            success=True,
            style_profile=StyleProfile(
                metadata=StyleMetadata(
                    style_id="extract_blue",
                    style_name="Extracted Blue Report Style",
                ),
                palette=ColourPalette(primary="#1f4e79"),
                chart=ChartStyle(background="#ffffff"),
            ),
            image_metadata=ImageMetadata(
                path="sample.png",
                format="PNG",
                width=1280,
                height=720,
                mode="RGB",
                aspect_ratio=16 / 9,
            ),
            palette_result=PaletteExtractionResult(
                colours=[
                    ExtractedColour("#1f4e79", (31, 78, 121), 55.0),
                ],
                background_colour="#ffffff",
                primary_colour="#1f4e79",
            ),
            deterministic_analysis=DeterministicImageStyleAnalysis(
                palette=PaletteExtractionResult(background_colour="#ffffff"),
                background_tone="light",
                contrast_level="high",
                chart_tone="corporate",
                grid_hint="light",
                label_density_hint="medium",
            ),
        )
    )

    panel = StyleExtractionPanel()

    assert "No style extracted" not in panel.summary_text(state)
    assert "Extracted Blue Report Style" in panel.summary_text(state)
