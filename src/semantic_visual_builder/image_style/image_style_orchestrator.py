"""Coordinate the image style extraction workflow."""

from __future__ import annotations

from pathlib import Path

from semantic_visual_builder.styles.style_validator import StyleValidator

from .image_loader import ImageLoader
from .image_metadata import build_image_metadata
from .image_style_analyzer import ImageStyleAnalyzer
from .palette_extractor import PaletteExtractor
from .style_draft_builder import StyleDraftBuilder
from .style_extraction_result import StyleExtractionResult
from .vlm_style_analyzer import VlmStyleAnalyzer


class ImageStyleExtractionOrchestrator:
    def __init__(
        self,
        image_loader: ImageLoader,
        palette_extractor: PaletteExtractor,
        image_style_analyzer: ImageStyleAnalyzer,
        style_draft_builder: StyleDraftBuilder,
        style_validator: StyleValidator,
        vlm_style_analyzer: VlmStyleAnalyzer | None = None,
    ):
        self.image_loader = image_loader
        self.palette_extractor = palette_extractor
        self.image_style_analyzer = image_style_analyzer
        self.style_draft_builder = style_draft_builder
        self.style_validator = style_validator
        self.vlm_style_analyzer = vlm_style_analyzer

    def extract_style(
        self,
        image_path: Path,
        style_name: str | None = None,
        use_vlm: bool = False,
        vlm_model: str | None = None,
    ) -> StyleExtractionResult:
        try:
            loaded_image = self.image_loader.load(image_path)
            image_metadata = build_image_metadata(loaded_image)
            palette_result = self.palette_extractor.extract_palette(loaded_image)
            deterministic_analysis = self.image_style_analyzer.analyze(
                loaded_image, palette_result
            )

            warnings = list(deterministic_analysis.warnings)
            vlm_analysis = None
            if use_vlm and self.vlm_style_analyzer is not None and vlm_model:
                vlm_analysis = self.vlm_style_analyzer.analyze_image_style(
                    vlm_model, image_path, deterministic_analysis
                )
                warnings.extend(vlm_analysis.warnings)
                if vlm_analysis.errors:
                    warnings.extend(vlm_analysis.errors)
            elif use_vlm:
                warnings.append(
                    "Vision analysis requested, but no vision analyzer is available."
                )

            suggested_name = style_name
            if not suggested_name:
                if vlm_analysis and vlm_analysis.suggested_name:
                    suggested_name = vlm_analysis.suggested_name
                else:
                    suggested_name = (
                        f"Extracted {deterministic_analysis.chart_tone.title()} Style"
                    )

            style_profile = self.style_draft_builder.build_style_profile(
                suggested_name,
                image_metadata,
                palette_result,
                deterministic_analysis,
                vlm_analysis,
            )
            validation = self.style_validator.validate_style(style_profile)
            if not validation.is_valid:
                errors = [message.message for message in validation.messages]
                return StyleExtractionResult(
                    success=False,
                    style_profile=style_profile,
                    image_metadata=image_metadata,
                    palette_result=palette_result,
                    deterministic_analysis=deterministic_analysis,
                    vlm_analysis=vlm_analysis,
                    warnings=warnings,
                    errors=errors,
                )
            return StyleExtractionResult(
                success=True,
                style_profile=style_profile,
                image_metadata=image_metadata,
                palette_result=palette_result,
                deterministic_analysis=deterministic_analysis,
                vlm_analysis=vlm_analysis,
                warnings=warnings,
            )
        except Exception as exc:
            return StyleExtractionResult(
                success=False,
                warnings=[],
                errors=[str(exc)],
            )
