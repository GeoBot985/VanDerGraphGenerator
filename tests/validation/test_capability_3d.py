"""Capability validator 3D rules."""

from semantic_visual_builder.knowledge.product_kb import ProductKnowledgeLoader
from semantic_visual_builder.planning.visual_plan_schema import VisualPlan
from semantic_visual_builder.utils.paths import get_kb_dir
from semantic_visual_builder.validation.capability_validator import (
    CapabilityValidator,
)


def _kb():
    return ProductKnowledgeLoader(get_kb_dir()).load()


def test_capability_validator_accepts_flat() -> None:
    plan = VisualPlan(visual_kind="chart", intent="compare", chart_type="bar")
    plan.style.chart_style = "flat"
    result = CapabilityValidator().validate_against_capabilities(plan, _kb())
    assert result.is_valid, result.messages


def test_capability_validator_accepts_soft_3d() -> None:
    plan = VisualPlan(visual_kind="chart", intent="compare", chart_type="bar")
    plan.style.chart_style = "soft_3d"
    plan.render_target.renderer = "plotly"
    result = CapabilityValidator().validate_against_capabilities(plan, _kb())
    assert result.is_valid, result.messages


def test_capability_validator_rejects_unknown_chart_style() -> None:
    plan = VisualPlan(visual_kind="chart", intent="compare", chart_type="bar")
    plan.style.chart_style = "holographic"
    plan.render_target.renderer = "plotly"
    result = CapabilityValidator().validate_against_capabilities(plan, _kb())
    assert not result.is_valid
    assert any("Chart style" in m.message for m in result.messages)


def test_capability_validator_flags_true_3d_with_wrong_renderer() -> None:
    plan = VisualPlan(visual_kind="chart", intent="compare", chart_type="bar")
    plan.style.chart_style = "true_3d"
    plan.render_target.renderer = "chartjs"
    result = CapabilityValidator().validate_against_capabilities(plan, _kb())
    assert not result.is_valid
    assert any("True 3D" in m.message for m in result.messages)


def test_capability_validator_rejects_negative_depth() -> None:
    plan = VisualPlan(visual_kind="chart", intent="compare", chart_type="bar")
    plan.style.chart_style = "soft_3d"
    plan.style.depth = -3
    plan.render_target.renderer = "plotly"
    result = CapabilityValidator().validate_against_capabilities(plan, _kb())
    assert not result.is_valid
    assert any("depth" in m.message for m in result.messages)
