"""Style schema tests."""

from semantic_visual_builder.styles.built_in_styles import list_builtin_style_profiles
from semantic_visual_builder.styles.style_schema import (
    ChartStyle,
    ColourPalette,
    DiagramStyle,
    RendererStyleHints,
    StyleMetadata,
    StyleProfile,
    TypographyStyle,
)


def test_style_profile_round_trip_serializes_cleanly() -> None:
    profile = StyleProfile(
        metadata=StyleMetadata(
            style_id="corporate_blue",
            style_name="Corporate Blue",
            description="Corporate style",
            author="QA",
            tags=["corporate", "blue"],
        ),
        palette=ColourPalette(
            primary="#1f4e79",
            secondary="#5b9bd5",
            accent="#70ad47",
            sequence=["#1f4e79", "#5b9bd5"],
        ),
        typography=TypographyStyle(font_family="Arial", title_size=18),
        chart=ChartStyle(background="#ffffff", grid="light"),
        diagram=DiagramStyle(direction="TD", node_fill="#d9eaf7"),
        renderer_hints=RendererStyleHints(plotly_template="plotly_white"),
    )

    payload = profile.to_dict()
    restored = StyleProfile.from_dict(payload)

    assert restored.style_id == "corporate_blue"
    assert restored.style_name == "Corporate Blue"
    assert restored.palette.primary == "#1f4e79"
    assert restored.diagram.direction == "TD"
    assert restored.renderer_hints.plotly_template == "plotly_white"


def test_builtin_style_profiles_have_expected_shape() -> None:
    styles = list_builtin_style_profiles()

    assert len(styles) == 4
    assert {style.style_id for style in styles} == {
        "corporate_blue",
        "minimal_grey",
        "presentation_green",
        "process_blue",
    }
