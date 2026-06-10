"""Style validator tests."""

from semantic_visual_builder.styles.style_schema import (
    ChartStyle,
    ColourPalette,
    StyleMetadata,
    StyleProfile,
    TypographyStyle,
)
from semantic_visual_builder.styles.style_validator import StyleValidator


def _style() -> StyleProfile:
    return StyleProfile(
        metadata=StyleMetadata(style_id="sample", style_name="Sample Style"),
        palette=ColourPalette(primary="#1f4e79"),
        typography=TypographyStyle(font_family="Arial"),
        chart=ChartStyle(grid="light", legend_position="right"),
        supported_visual_kinds=["chart", "diagram"],
        supported_renderers=["plotly", "mermaid"],
    )


def test_valid_style_profile_passes_validation() -> None:
    result = StyleValidator().validate_style(_style())

    assert result.is_valid is True


def test_invalid_style_profile_is_rejected() -> None:
    style = _style()
    style.metadata.schema_version = "2.0"
    style.palette.primary = "javascript:alert(1)"
    style.supported_renderers = ["plotly", "unknown"]

    result = StyleValidator().validate_style(style)

    assert result.is_valid is False
    assert any("schema_version" in item.message for item in result.messages)
    assert any("Unsafe style value" in item.message for item in result.messages)
    assert any("Unsupported renderer" in item.message for item in result.messages)
