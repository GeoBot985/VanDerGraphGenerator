"""Image loader tests."""

from pathlib import Path

import pytest
from PIL import Image

from semantic_visual_builder.image_style.image_loader import ImageLoader


def _make_image(path: Path, mode: str = "RGBA") -> None:
    image = Image.new(mode, (64, 32), (255, 255, 255, 255))
    image.save(path)


def test_png_loads_and_converts_to_rgb(tmp_path: Path) -> None:
    path = tmp_path / "sample.png"
    _make_image(path)

    loaded = ImageLoader().load(path)

    assert loaded.path == path
    assert loaded.format == "PNG"
    assert loaded.width == 64
    assert loaded.height == 32
    assert loaded.mode == "RGBA"
    assert loaded.image.mode == "RGB"


def test_jpg_loads_if_supported(tmp_path: Path) -> None:
    path = tmp_path / "sample.jpg"
    image = Image.new("RGB", (32, 16), (200, 200, 200))
    image.save(path)

    loaded = ImageLoader().load(path)

    assert loaded.format == "JPEG"
    assert loaded.image.mode == "RGB"


def test_unsupported_extension_is_rejected(tmp_path: Path) -> None:
    path = tmp_path / "sample.txt"
    path.write_text("not an image", encoding="utf-8")

    with pytest.raises(ValueError):
        ImageLoader().load(path)


def test_missing_file_raises_file_not_found(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        ImageLoader().load(tmp_path / "missing.png")
