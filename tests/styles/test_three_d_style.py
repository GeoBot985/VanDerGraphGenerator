"""Tests for the ThreeDStyle field on StyleProfile and its applier."""

from __future__ import annotations

from semantic_visual_builder.planning.visual_plan_schema import VisualPlan
from semantic_visual_builder.styles.built_in_styles import list_builtin_style_profiles
from semantic_visual_builder.styles.style_applier import StyleApplier
from semantic_visual_builder.styles.style_schema import (
    ChartStyle,
    ColourPalette,
    DiagramStyle,
    StyleMetadata,
    StyleProfile,
    ThreeDStyle,
    TypographyStyle,
)
from semantic_visual_builder.styles.style_summary import summarize_style
from semantic_visual_builder.styles.style_validator import StyleValidator


def _plan() -> VisualPlan:
    return VisualPlan(visual_kind="chart", intent="compare")


def _style() -> StyleProfile:
    return StyleProfile(
        metadata=StyleMetadata(style_id="x", style_name="X"),
        palette=ColourPalette(primary="#1f4e79"),
        typography=TypographyStyle(),
        chart=ChartStyle(),
        diagram=DiagramStyle(),
        three_d=ThreeDStyle(chart_style="true_3d", depth=20, lighting="soft"),
    )


def test_applier_records_chart_style_from_profile() -> None:
    plan = _plan()
    StyleApplier().apply_style(plan, _style())
    assert plan.style.chart_style == "true_3d"
    assert plan.style.depth == 20
    assert plan.style.lighting == "soft"


def test_applier_keeps_existing_style_when_profile_omits_three_d() -> None:
    plan = _plan()
    plan.style.chart_style = "soft_3d"
    profile = StyleProfile(
        metadata=StyleMetadata(style_id="y", style_name="Y"),
        palette=ColourPalette(),
        typography=TypographyStyle(),
        chart=ChartStyle(),
        diagram=DiagramStyle(),
    )
    StyleApplier().apply_style(plan, profile)
    assert plan.style.chart_style == "soft_3d"


def test_summary_includes_3d_treatment() -> None:
    summary = summarize_style(_style())
    assert "3D treatment" in summary
    assert "true_3d" in summary


def test_validator_accepts_supported_chart_styles() -> None:
    for style_value in ("flat", "soft_3d", "true_3d"):
        style = _style()
        style.three_d.chart_style = style_value
        result = StyleValidator().validate_style(style)
        assert result.is_valid, (style_value, result.messages)


def test_validator_rejects_unknown_chart_style() -> None:
    style = _style()
    style.three_d.chart_style = "holographic"
    result = StyleValidator().validate_style(style)
    assert not result.is_valid
    assert any("chart_style" in m.message for m in result.messages)


def test_validator_rejects_out_of_range_perspective() -> None:
    style = _style()
    style.three_d.perspective = 1.5
    result = StyleValidator().validate_style(style)
    assert not result.is_valid
    assert any("perspective" in m.message for m in result.messages)


def test_builtin_catalog_includes_flat_soft_and_true_3d_styles() -> None:
    styles = list_builtin_style_profiles()
    flat_styles = [s for s in styles if (s.three_d.chart_style or "flat") == "flat"]
    soft_styles = [s for s in styles if s.three_d.chart_style == "soft_3d"]
    true_styles = [s for s in styles if s.three_d.chart_style == "true_3d"]
    assert len(flat_styles) >= 10
    assert len(soft_styles) >= 2
    assert len(true_styles) >= 2
    # Every built-in must have a valid 3D treatment value.
    for s in styles:
        assert (s.three_d.chart_style or "flat") in {"flat", "soft_3d", "true_3d"}
