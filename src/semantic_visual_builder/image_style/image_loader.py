"""Image loading helpers for style extraction."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from PIL import Image


@dataclass
class LoadedImage:
    path: Path
    image: Image.Image
    format: str | None
    width: int
    height: int
    mode: str


class ImageLoader:
    supported_extensions = {".png", ".jpg", ".jpeg", ".webp"}

    def load(self, path: Path) -> LoadedImage:
        if not path.exists():
            raise FileNotFoundError(f"Image file not found: {path}")
        if path.suffix.lower() not in self.supported_extensions:
            raise ValueError(
                f"Unsupported image format: {path.suffix}. Supported: "
                f"{', '.join(sorted(self.supported_extensions))}"
            )
        with Image.open(path) as image:
            loaded_format = image.format
            width, height = image.size
            mode = image.mode
            rgb_image = image.convert("RGB")
        return LoadedImage(
            path=path,
            image=rgb_image,
            format=loaded_format,
            width=width,
            height=height,
            mode=mode,
        )
