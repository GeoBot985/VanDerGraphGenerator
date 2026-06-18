"""Tests for chart_style detection in the deterministic fallback mapper."""

from __future__ import annotations

from semantic_visual_builder.planning.deterministic_fallback_mapper import (
    DeterministicFallbackMapper,
)


def test_detect_chart_style_promotes_true_3d_phrases() -> None:
    mapper = DeterministicFallbackMapper()
    assert mapper.detect_chart_style("Show a true 3d bar chart") == "true_3d"
    assert mapper.detect_chart_style("Create an immersive 3d scatter") == "true_3d"
    assert mapper.detect_chart_style("Make a fully 3d pie chart") == "true_3d"
    assert mapper.detect_chart_style("interactive 3d line chart") == "true_3d"


def test_detect_chart_style_promotes_soft_3d_phrases() -> None:
    mapper = DeterministicFallbackMapper()
    assert mapper.detect_chart_style("Show a soft 3d bar chart") == "soft_3d"
    assert mapper.detect_chart_style("extruded bar chart") == "soft_3d"
    assert mapper.detect_chart_style("raised bar chart") == "soft_3d"
    # A plain "3d" falls back to the cheaper soft_3d treatment.
    assert mapper.detect_chart_style("Show a 3d bar chart") == "soft_3d"


def test_detect_chart_style_returns_flat_or_none_when_no_3d() -> None:
    mapper = DeterministicFallbackMapper()
    assert mapper.detect_chart_style("Show a bar chart") is None
    assert mapper.detect_chart_style("Plain flat bar chart") == "flat"


def test_map_request_to_plan_records_3d_treatment() -> None:
    mapper = DeterministicFallbackMapper()
    plan = mapper.map_request_to_plan("Show a true 3d bar chart of amount by region")
    assert plan.style.chart_style == "true_3d"
    assert any("3D treatment" in note for note in plan.notes)

    plan_soft = mapper.map_request_to_plan("extruded bar chart")
    assert plan_soft.style.chart_style == "soft_3d"
    assert any("3D treatment" in note for note in plan_soft.notes)


def test_map_request_to_plan_does_not_force_3d_without_hint() -> None:
    mapper = DeterministicFallbackMapper()
    plan = mapper.map_request_to_plan("Show transactions per week")
    assert plan.style.chart_style is None
