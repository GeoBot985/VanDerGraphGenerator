"""Built-in composite style profile tests."""

from semantic_visual_builder.styles.built_in_styles import list_builtin_style_profiles
from semantic_visual_builder.styles.style_validator import StyleValidator

_EXPECTED_IDS = [
    "editorial_serif",
    "magazine_bold",
    "boardroom",
    "minimal_swiss",
    "technical_report",
    "academic_paper",
    "dashboard_dark",
    "terminal_neon",
    "pastel_soft",
    "marketing_punch",
    "ocean_cool",
    "sunset_warm",
    "colorblind_safe",
    "high_contrast_print",
    # --- 3D / soft_3d / true_3d variants (Sprint 13) ---
    "soft_3d_gloss",
    "soft_3d_boardroom",
    "true_3d_cosmic",
    "true_3d_warehouse",
    "true_3d_pastel",
]


def test_builtin_style_ids_match_the_composite_set() -> None:
    ids = [style.style_id for style in list_builtin_style_profiles()]
    assert ids == _EXPECTED_IDS
    assert len(ids) == len(set(ids)), "built-in style ids must be unique"


def test_all_builtin_styles_validate() -> None:
    validator = StyleValidator()
    for style in list_builtin_style_profiles():
        result = validator.validate_style(style)
        assert result.is_valid, f"{style.style_id}: {[m.message for m in result.messages]}"


def test_each_style_is_a_full_composite_not_just_a_palette() -> None:
    """Every built-in style must define typography, surface and a palette so
    that switching a style changes the whole feel, not just the colours."""
    for style in list_builtin_style_profiles():
        typo = style.typography
        chart = style.chart
        assert typo.font_family, f"{style.style_id} has no font_family"
        assert typo.title_size is not None, f"{style.style_id} has no title_size"
        assert typo.label_size is not None, f"{style.style_id} has no label_size"
        assert chart.background is not None, f"{style.style_id} has no background"
        assert chart.grid in {"none", "light", "medium"}, f"{style.style_id} bad grid"
        assert chart.legend_position in {"right", "bottom", "none"}, f"{style.style_id} bad legend"
        assert style.palette.sequence, f"{style.style_id} has no colour sequence"


def test_styles_have_distinct_typographic_identities() -> None:
    """The set should not be a single font/size repeated; styles must differ in
    font family, weight, and title size so they read as different design systems."""
    styles = list_builtin_style_profiles()
    families = {(s.typography.font_family, s.typography.font_weight) for s in styles}
    title_sizes = {s.typography.title_size for s in styles}
    assert len(families) >= 4, f"too few distinct font identities: {families}"
    assert len(title_sizes) >= 4, f"too few distinct title sizes: {title_sizes}"
