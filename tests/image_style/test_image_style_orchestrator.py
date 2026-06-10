"""Image style orchestrator tests."""

from pathlib import Path

from PIL import Image, ImageDraw

from semantic_visual_builder.image_style.image_loader import ImageLoader
from semantic_visual_builder.image_style.image_style_analyzer import ImageStyleAnalyzer
from semantic_visual_builder.image_style.image_style_orchestrator import (
    ImageStyleExtractionOrchestrator,
)
from semantic_visual_builder.image_style.palette_extractor import PaletteExtractor
from semantic_visual_builder.image_style.style_draft_builder import StyleDraftBuilder
from semantic_visual_builder.styles.style_validator import StyleValidator


class RejectingValidator:
    def validate_style(self, style):  # noqa: ANN001
        from semantic_visual_builder.validation.validation_result import (
            ValidationMessage,
            ValidationResult,
            ValidationSeverity,
        )

        return ValidationResult(
            messages=[
                ValidationMessage(
                    ValidationSeverity.ERROR, "Style is intentionally invalid."
                )
            ]
        )


def _make_image(path: Path) -> None:
    image = Image.new("RGB", (400, 240), "#ffffff")
    ImageDraw.Draw(image).rectangle([50, 40, 180, 200], fill="#1f4e79")
    ImageDraw.Draw(image).rectangle([220, 80, 350, 200], fill="#70ad47")
    image.save(path)


def test_deterministic_style_extraction_succeeds(tmp_path: Path) -> None:
    path = tmp_path / "sample.png"
    _make_image(path)
    orchestrator = ImageStyleExtractionOrchestrator(
        ImageLoader(),
        PaletteExtractor(),
        ImageStyleAnalyzer(),
        StyleDraftBuilder(),
        StyleValidator(),
    )

    result = orchestrator.extract_style(path)

    assert result.success is True
    assert result.style_profile is not None
    assert result.palette_result is not None


def test_vlm_failure_falls_back_to_deterministic_result(tmp_path: Path) -> None:
    path = tmp_path / "sample.png"
    _make_image(path)
    orchestrator = ImageStyleExtractionOrchestrator(
        ImageLoader(),
        PaletteExtractor(),
        ImageStyleAnalyzer(),
        StyleDraftBuilder(),
        StyleValidator(),
    )

    result = orchestrator.extract_style(path, use_vlm=True, vlm_model="vision-model")

    assert result.success is True
    assert result.warnings


def test_invalid_style_validation_is_reported(tmp_path: Path) -> None:
    path = tmp_path / "sample.png"
    _make_image(path)
    orchestrator = ImageStyleExtractionOrchestrator(
        ImageLoader(),
        PaletteExtractor(),
        ImageStyleAnalyzer(),
        StyleDraftBuilder(),
        RejectingValidator(),
    )

    result = orchestrator.extract_style(path)

    assert result.success is False
    assert result.errors
