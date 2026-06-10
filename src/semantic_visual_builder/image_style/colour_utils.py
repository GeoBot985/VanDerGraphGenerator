"""Colour utility helpers for image style extraction."""

from __future__ import annotations

from math import sqrt


def rgb_to_hex(rgb: tuple[int, int, int]) -> str:
    return "#{:02x}{:02x}{:02x}".format(*rgb)


def colour_distance(a: tuple[int, int, int], b: tuple[int, int, int]) -> float:
    return sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2 + (a[2] - b[2]) ** 2)


def brightness(rgb: tuple[int, int, int]) -> float:
    return 0.299 * rgb[0] + 0.587 * rgb[1] + 0.114 * rgb[2]


def saturation_approx(rgb: tuple[int, int, int]) -> float:
    maximum = max(rgb)
    minimum = min(rgb)
    if maximum == 0:
        return 0.0
    return (maximum - minimum) / maximum


def is_near_white(rgb: tuple[int, int, int]) -> bool:
    return brightness(rgb) >= 235 and saturation_approx(rgb) <= 0.15


def is_near_black(rgb: tuple[int, int, int]) -> bool:
    return brightness(rgb) <= 20
