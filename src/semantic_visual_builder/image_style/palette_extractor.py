"""Deterministic palette extraction from images."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from typing import Iterable

from PIL import Image

from .colour_utils import (
    brightness,
    colour_distance,
    is_near_black,
    is_near_white,
    rgb_to_hex,
    saturation_approx,
)
from .image_loader import LoadedImage


@dataclass
class ExtractedColour:
    hex_value: str
    rgb: tuple[int, int, int]
    percentage: float
    role_hint: str | None = None


@dataclass
class PaletteExtractionResult:
    colours: list[ExtractedColour] = field(default_factory=list)
    background_colour: str | None = None
    primary_colour: str | None = None
    accent_colour: str | None = None
    neutral_colour: str | None = None
    warnings: list[str] = field(default_factory=list)


class PaletteExtractor:
    def extract_palette(
        self,
        loaded_image: LoadedImage,
        max_colours: int = 8,
    ) -> PaletteExtractionResult:
        if max_colours < 1:
            raise ValueError("max_colours must be at least 1")

        result = PaletteExtractionResult()
        analysis_image = loaded_image.image.convert("RGB")
        analysis_image = analysis_image.copy()
        analysis_image.thumbnail((400, 400))

        background_rgb = self._estimate_background(analysis_image)
        quantized = analysis_image.quantize(
            colors=max(2, max_colours), method=Image.Quantize.FASTOCTREE
        )
        palette = quantized.getpalette() or []
        counts = quantized.getcolors() or []
        total_pixels = sum(count for count, _ in counts) or 1

        ranked: list[ExtractedColour] = []
        for count, index in sorted(counts, reverse=True):
            rgb = self._palette_index_to_rgb(palette, index)
            if self._is_duplicate(rgb, ranked):
                continue
            percentage = round((count / total_pixels) * 100, 2)
            role_hint = self._role_hint(rgb, background_rgb)
            ranked.append(
                ExtractedColour(
                    hex_value=rgb_to_hex(rgb),
                    rgb=rgb,
                    percentage=percentage,
                    role_hint=role_hint,
                )
            )
            if len(ranked) >= max_colours:
                break

        if not ranked:
            result.warnings.append("No dominant colours could be extracted.")
            return result

        result.colours = ranked
        result.background_colour = rgb_to_hex(background_rgb)
        result.primary_colour = self._pick_primary(ranked, background_rgb)
        result.accent_colour = self._pick_accent(
            ranked, background_rgb, result.primary_colour
        )
        result.neutral_colour = self._pick_neutral(ranked, background_rgb)
        if len(ranked) < 3:
            result.warnings.append(
                "Palette is sparse; style inference may be approximate."
            )
        return result

    def _estimate_background(self, image: Image.Image) -> tuple[int, int, int]:
        width, height = image.size
        if width == 0 or height == 0:
            return (255, 255, 255)
        corners: list[tuple[int, int, int]] = [
            tuple(image.getpixel((0, 0)))[:3],  # type: ignore[misc]
            tuple(image.getpixel((width - 1, 0)))[:3],  # type: ignore[misc]
            tuple(image.getpixel((0, height - 1)))[:3],  # type: ignore[misc]
            tuple(image.getpixel((width - 1, height - 1)))[:3],  # type: ignore[misc]
        ]
        consensus = self._corner_consensus(corners)
        if consensus is not None:
            return consensus
        samples: list[tuple[int, int, int]] = list(corners)
        step = max(1, min(width, height) // 20)
        sample_points: set[tuple[int, int]] = set()
        for x in range(0, width, step):
            sample_points.add((x, 0))
            sample_points.add((x, height - 1))
        for y in range(0, height, step):
            sample_points.add((0, y))
            sample_points.add((width - 1, y))
        for x, y in sample_points:
            samples.append(tuple(image.getpixel((x, y)))[:3])  # type: ignore[misc]
        return Counter(samples).most_common(1)[0][0]

    def _corner_consensus(
        self, corners: list[tuple[int, int, int]]
    ) -> tuple[int, int, int] | None:
        for candidate in corners:
            if sum(colour_distance(candidate, c) <= 30 for c in corners) >= 3:
                return candidate
        return None

    def _palette_index_to_rgb(
        self, palette: list[int], index: int
    ) -> tuple[int, int, int]:
        offset = index * 3
        return tuple(palette[offset : offset + 3])  # type: ignore[return-value]

    def _is_duplicate(
        self, rgb: tuple[int, int, int], colours: Iterable[ExtractedColour]
    ) -> bool:
        return any(colour_distance(rgb, existing.rgb) < 22 for existing in colours)

    def _role_hint(
        self, rgb: tuple[int, int, int], background_rgb: tuple[int, int, int]
    ) -> str | None:
        if colour_distance(rgb, background_rgb) < 20 or is_near_white(rgb):
            return "background"
        if saturation_approx(rgb) < 0.15 or is_near_black(rgb):
            return "neutral"
        if brightness(rgb) > brightness(background_rgb):
            return "accent"
        return "primary"

    def _pick_primary(
        self,
        colours: list[ExtractedColour],
        background_rgb: tuple[int, int, int],
    ) -> str | None:
        candidates = [
            colour
            for colour in colours
            if colour.role_hint not in ("background",)
            and not is_near_white(colour.rgb)
            and not is_near_black(colour.rgb)
            and colour_distance(colour.rgb, background_rgb) >= 25
        ]
        if candidates:
            candidates.sort(key=lambda c: saturation_approx(c.rgb), reverse=True)
            return candidates[0].hex_value
        for colour in colours:
            if colour.role_hint == "background":
                continue
            if colour_distance(colour.rgb, background_rgb) >= 20:
                return colour.hex_value
        return colours[0].hex_value if colours else None

    def _pick_accent(
        self,
        colours: list[ExtractedColour],
        background_rgb: tuple[int, int, int],
        primary_colour: str | None,
    ) -> str | None:
        primary_rgb = self._hex_to_rgb(primary_colour) if primary_colour else None
        candidates = [
            colour
            for colour in colours
            if colour.hex_value != primary_colour
            and colour.role_hint != "background"
            and colour_distance(colour.rgb, background_rgb) >= 20
        ]
        if primary_rgb is not None:
            candidates.sort(
                key=lambda colour: colour_distance(colour.rgb, primary_rgb),
                reverse=True,
            )
        if candidates:
            return candidates[0].hex_value
        return None

    def _pick_neutral(
        self,
        colours: list[ExtractedColour],
        background_rgb: tuple[int, int, int],
    ) -> str | None:
        neutrals = [
            colour
            for colour in colours
            if colour.role_hint == "neutral"
            and colour_distance(colour.rgb, background_rgb) >= 8
        ]
        if neutrals:
            return neutrals[0].hex_value
        return None

    def _hex_to_rgb(self, hex_value: str | None) -> tuple[int, int, int] | None:
        if not hex_value:
            return None
        text = hex_value.lstrip("#")
        if len(text) != 6:
            return None
        return tuple(int(text[index : index + 2], 16) for index in (0, 2, 4))
