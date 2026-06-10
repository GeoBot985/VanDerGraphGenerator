"""Visual plan schema tests."""

from semantic_visual_builder.planning.visual_plan_schema import VisualPlan


def test_visual_plan_dataclass() -> None:
    plan = VisualPlan(visual_kind="bar", intent="compare_categories")
    assert plan.renderer is None
