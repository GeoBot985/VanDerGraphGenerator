"""Image metadata tests."""

from pathlib import Path

from PIL import Image

from semantic_visual_builder.image_style.image_loader import ImageLoader
from semantic_visual_builder.image_style.image_metadata import build_image_metadata


def test_image_metadata_includes_dimensions_and_aspect_ratio(tmp_path: Path) -> None:
    path = tmp_path / "sample.png"
    Image.new("RGB", (128, 64), (255, 255, 255)).save(path)

    loaded = ImageLoader().load(path)
    metadata = build_image_metadata(loaded)

    assert metadata.path == str(path)
    assert metadata.width == 128
    assert metadata.height == 64
    assert metadata.mode == "RGB"
    assert metadata.aspect_ratio == 2.0
