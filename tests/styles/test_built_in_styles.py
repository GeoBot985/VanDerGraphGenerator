"""Built-in style profile tests."""

from semantic_visual_builder.styles.built_in_styles import list_builtin_style_profiles


def test_builtin_style_ids_are_stable() -> None:
    styles = list_builtin_style_profiles()

    assert [style.style_id for style in styles] == [
        "corporate_blue",
        "minimal_grey",
        "presentation_green",
        "process_blue",
    ]
