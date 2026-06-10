"""Refinement engine tests."""

from semantic_visual_builder.planning.refinement_engine import RefinementEngine
from semantic_visual_builder.planning.visual_plan_schema import StyleIntent, VisualPlan


def _base_plan() -> VisualPlan:
    return VisualPlan(visual_kind="chart", intent="compare_categories", chart_type="bar", style=StyleIntent(title="Original"))


def test_make_it_a_bar_chart_updates_chart_type() -> None:
    updated = RefinementEngine().apply_refinement(_base_plan(), "Make it a bar chart")
    assert updated.chart_type == "bar"


def test_make_it_horizontal_updates_chart_type() -> None:
    updated = RefinementEngine().apply_refinement(_base_plan(), "Make it horizontal")
    assert updated.chart_type == "horizontal_bar"


def test_title_refinement_updates_title() -> None:
    updated = RefinementEngine().apply_refinement(_base_plan(), "Title should be Sales by Region")
    assert updated.style.title == "Sales by Region"


def test_highlight_refinement_updates_highlights() -> None:
    updated = RefinementEngine().apply_refinement(_base_plan(), "Highlight Gauteng")
    assert updated.style.highlights == {"value": "Gauteng"}


def test_refinement_does_not_mutate_original_plan() -> None:
    original = _base_plan()
    updated = RefinementEngine().apply_refinement(original, "Change title to Updated")
    assert original.style.title == "Original"
    assert updated.style.title == "Updated"
