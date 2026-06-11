"""Tests for style summary visibility in the style panel."""

from semantic_visual_builder.state.app_state import AppState
from semantic_visual_builder.ui.style_panel import StylePanel
from semantic_visual_builder.styles.style_schema import (
    ChartStyle,
    ColourPalette,
    StyleMetadata,
    StyleProfile,
    TypographyStyle,
)


def test_style_summary_includes_background_and_sequence() -> None:
    state = AppState()
    state.set_active_style_profile(
        StyleProfile(
            metadata=StyleMetadata(style_id="dark_and_neon", style_name="dark and neon"),
            palette=ColourPalette(
                primary="#00e5ff",
                accent="#ff00d4",
                sequence=["#00e5ff", "#ff00d4", "#7c4dff"],
            ),
            typography=TypographyStyle(font_family="Arial", title_size=18),
            chart=ChartStyle(
                background="#111827",
                plot_background="#111827",
                grid="light",
                legend_position="right",
            ),
        )
    )

    text = StylePanel().summary_text(state)

    assert "Background: #111827" in text
    assert "Plot background: #111827" in text
    assert "Sequence: #00e5ff, #ff00d4, #7c4dff" in text
