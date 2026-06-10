"""Derived metadata for loaded images."""

from __future__ import annotations

from dataclasses import dataclass

from .image_loader import LoadedImage


@dataclass
class ImageMetadata:
    path: str
    format: str | None
    width: int
    height: int
    mode: str
    aspect_ratio: float


def build_image_metadata(loaded_image: LoadedImage) -> ImageMetadata:
    aspect_ratio = (
        loaded_image.width / loaded_image.height if loaded_image.height else 0.0
    )
    return ImageMetadata(
        path=str(loaded_image.path),
        format=loaded_image.format,
        width=loaded_image.width,
        height=loaded_image.height,
        mode=loaded_image.mode,
        aspect_ratio=aspect_ratio,
    )
