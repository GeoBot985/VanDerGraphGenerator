"""Built-in style profile tests."""

from semantic_visual_builder.styles.built_in_styles import list_builtin_style_profiles
from semantic_visual_builder.styles.style_validator import StyleValidator

_ORIGINAL_FOUR = [
    "corporate_blue",
    "minimal_grey",
    "presentation_green",
    "process_blue",
]

_ADDED_SCHEMES = [
    "dark_slate",
    "midnight_neon",
    "vibrant",
    "colorblind_safe",
    "ocean",
    "sunset",
    "forest",
    "pastel",
    "monochrome_blue",
    "high_contrast",
    "solarized",
    "warm_earth",
    # expanded set
    "nordic",
    "rose_gold",
    "cyberpunk",
    "terra_cotta",
    "lavender_mist",
    "matcha",
    "deep_space",
    "retro",
    "berry",
    "executive",
    "arctic",
    "autumn",
    "candy",
    "print_friendly",
    "data_science",
    "teal_coral",
]

_MIN_BUILTIN_COUNT = 30


def test_builtin_style_ids_are_stable() -> None:
    styles = list_builtin_style_profiles()

    # Original four remain first, in order, so existing references stay valid.
    assert [style.style_id for style in styles[:4]] == _ORIGINAL_FOUR


def test_added_colour_schemes_are_present() -> None:
    ids = [style.style_id for style in list_builtin_style_profiles()]

    for scheme_id in _ADDED_SCHEMES:
        assert scheme_id in ids, f"missing built-in style: {scheme_id}"
    assert len(ids) == len(set(ids)), "built-in style ids must be unique"
    assert len(ids) >= _MIN_BUILTIN_COUNT, f"expected at least {_MIN_BUILTIN_COUNT} built-in styles, got {len(ids)}"


def test_all_builtin_styles_validate() -> None:
    validator = StyleValidator()

    for style in list_builtin_style_profiles():
        result = validator.validate_style(style)
        assert result.is_valid, f"{style.style_id}: {[m.message for m in result.messages]}"
