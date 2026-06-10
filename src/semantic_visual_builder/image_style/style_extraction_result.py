"""Result object for image style extraction."""

from __future__ import annotations

from dataclasses import dataclass, field

from semantic_visual_builder.styles.style_schema import StyleProfile

from .image_metadata import ImageMetadata
from .image_style_analyzer import DeterministicImageStyleAnalysis
from .palette_extractor import PaletteExtractionResult
from .vlm_style_analyzer import VlmStyleAnalysis


@dataclass
class StyleExtractionResult:
    success: bool
    style_profile: StyleProfile | None = None
    image_metadata: ImageMetadata | None = None
    palette_result: PaletteExtractionResult | None = None
    deterministic_analysis: DeterministicImageStyleAnalysis | None = None
    vlm_analysis: VlmStyleAnalysis | None = None
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
