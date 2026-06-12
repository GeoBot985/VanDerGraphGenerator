"""Heuristic image style analysis."""

from __future__ import annotations

from dataclasses import dataclass, field

from PIL import ImageFilter

from .colour_utils import brightness, colour_distance, saturation_approx
from .image_loader import LoadedImage
from .palette_extractor import PaletteExtractionResult


@dataclass
class DeterministicImageStyleAnalysis:
    palette: PaletteExtractionResult
    background_tone: str
    contrast_level: str
    chart_tone: str
    grid_hint: str
    label_density_hint: str
    text_colour_hint: str | None = None
    warnings: list[str] = field(default_factory=list)


class ImageStyleAnalyzer:
    def analyze(
        self,
        loaded_image: LoadedImage,
        palette_result: PaletteExtractionResult,
    ) -> DeterministicImageStyleAnalysis:
        background_rgb = self._hex_to_rgb(
            palette_result.background_colour or palette_result.primary_colour
        ) or (255, 255, 255)
        primary_rgb = self._hex_to_rgb(palette_result.primary_colour) or background_rgb
        accent_rgb = self._hex_to_rgb(palette_result.accent_colour)
        neutral_rgb = self._hex_to_rgb(palette_result.neutral_colour)

        bg_brightness = brightness(background_rgb)
        if bg_brightness > 200:
            background_tone = "light"
            text_colour_hint = "#000000"
        elif bg_brightness < 80:
            background_tone = "dark"
            text_colour_hint = "#ffffff"
        else:
            background_tone = "neutral"
            text_colour_hint = (
                "#000000" if bg_brightness >= 128 else "#ffffff"
            )
        contrast_level = self._contrast_level(background_rgb, primary_rgb, accent_rgb)
        chart_tone = self._chart_tone(
            background_rgb,
            primary_rgb,
            accent_rgb,
            neutral_rgb,
            palette_result,
        )
        grid_hint = self._grid_hint(background_tone, neutral_rgb)
        label_density_hint = self._estimate_label_density(loaded_image)
        warnings = list(palette_result.warnings)
        if loaded_image.width < 320 or loaded_image.height < 240:
            warnings.append("Image is small; style inference may be approximate.")
        return DeterministicImageStyleAnalysis(
            palette=palette_result,
            background_tone=background_tone,
            contrast_level=contrast_level,
            chart_tone=chart_tone,
            grid_hint=grid_hint,
            label_density_hint=label_density_hint,
            text_colour_hint=text_colour_hint,
            warnings=warnings,
        )

    def _contrast_level(
        self,
        background_rgb: tuple[int, int, int],
        primary_rgb: tuple[int, int, int],
        accent_rgb: tuple[int, int, int] | None,
    ) -> str:
        candidates = [colour_distance(background_rgb, primary_rgb)]
        if accent_rgb is not None:
            candidates.append(colour_distance(background_rgb, accent_rgb))
        maximum = max(candidates)
        if maximum >= 140:
            return "high"
        if maximum >= 80:
            return "medium"
        return "low"

    def _chart_tone(
        self,
        background_rgb: tuple[int, int, int],
        primary_rgb: tuple[int, int, int],
        accent_rgb: tuple[int, int, int] | None,
        neutral_rgb: tuple[int, int, int] | None,
        palette_result: PaletteExtractionResult,
    ) -> str:
        primary_blue_bias = (
            primary_rgb[2] >= primary_rgb[0] and primary_rgb[2] >= primary_rgb[1]
        )
        greyish_neutral = (
            neutral_rgb is not None and saturation_approx(neutral_rgb) <= 0.15
        )
        accent_is_saturated = (
            accent_rgb is not None and saturation_approx(accent_rgb) >= 0.35
        )
        if primary_blue_bias and greyish_neutral and brightness(background_rgb) >= 140:
            return "corporate"
        if accent_is_saturated or any(
            saturation_approx(colour.rgb) >= 0.45 for colour in palette_result.colours
        ):
            return "presentation"
        return "report"

    def _grid_hint(
        self,
        background_tone: str,
        neutral_rgb: tuple[int, int, int] | None,
    ) -> str:
        if background_tone == "dark":
            return "none"
        if background_tone == "light" and neutral_rgb is not None:
            return "light"
        return "medium"

    def _estimate_label_density(self, loaded_image: LoadedImage) -> str:
        thumb = loaded_image.image.convert("L").copy()
        thumb.thumbnail((120, 120))
        edges = thumb.filter(ImageFilter.FIND_EDGES)
        pixels = list(edges.getdata())
        if not pixels:
            return "low"
        edge_count = sum(1 for p in pixels if p > 25)
        ratio = edge_count / len(pixels)
        if ratio > 0.14:
            return "high"
        if ratio > 0.05:
            return "medium"
        return "low"

    def _hex_to_rgb(self, hex_value: str | None) -> tuple[int, int, int] | None:
        if not hex_value:
            return None
        text = hex_value.lstrip("#")
        if len(text) != 6:
            return None
        return tuple(int(text[index : index + 2], 16) for index in (0, 2, 4))
