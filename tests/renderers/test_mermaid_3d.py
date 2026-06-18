"""Tests for the 3D plumbing in the Mermaid style adapter and renderer."""

from __future__ import annotations

from unittest.mock import MagicMock

from semantic_visual_builder.planning.diagram_plan_builder import DiagramPlanBuilder
from semantic_visual_builder.renderers.mermaid_renderer import MermaidRenderer
from semantic_visual_builder.renderers.mermaid_style_adapter import (
    MermaidStyleAdapter,
    is_mermaid_3d,
    mermaid_chart_style,
)


def _make_plan(
    background: str | None = None,
    primary: str | None = None,
    chart_style: str | None = None,
) -> MagicMock:
    plan = MagicMock()
    plan.style.background = background or "#ffffff"
    plan.style.chart_style = chart_style
    plan.style.orientation = None
    plan.style.diagram_direction = "TD"
    plan.style.palette = {
        "primary": primary,
        "secondary": None,
        "accent": None,
        "neutral": None,
        "class_defs": {},
    }
    return plan


SIMPLE_FLOWCHART = "flowchart TD\n    A --> B"


class TestMermaidChartStyle:
    def setup_method(self) -> None:
        self.adapter = MermaidStyleAdapter()

    def test_mermaid_chart_style_defaults_to_flat(self) -> None:
        plan = _make_plan()
        assert mermaid_chart_style(plan) == "flat"
        assert is_mermaid_3d(plan) is False

    def test_mermaid_chart_style_recognises_soft_3d(self) -> None:
        plan = _make_plan(chart_style="soft_3d")
        assert mermaid_chart_style(plan) == "soft_3d"
        assert is_mermaid_3d(plan) is True

    def test_soft_3d_adds_opacity_to_class_defs(self) -> None:
        plan = _make_plan(primary="#1f4e79", chart_style="soft_3d")
        result = self.adapter.apply_style_to_mermaid(SIMPLE_FLOWCHART, plan)
        assert "fill-opacity:0.92" in result

    def test_true_3d_adds_shadow_and_bold_stroke_to_class_defs(self) -> None:
        plan = _make_plan(primary="#1f4e79", chart_style="true_3d")
        result = self.adapter.apply_style_to_mermaid(SIMPLE_FLOWCHART, plan)
        assert "stroke-width:3px" in result
        assert "fill-opacity:0.96" in result
        assert "shadow:" in result


class TestMermaidRenderer3DShapes:
    def test_flat_uses_rectangle_node(self) -> None:
        plan = DiagramPlanBuilder().build_basic_flowchart(
            "A user submits a request. An analyst reviews it."
        )
        plan.style.chart_style = "flat"
        out = MermaidRenderer().render(plan)
        assert "A[A user submits a request]" in out.content

    def test_soft_3d_uses_round_edge_node(self) -> None:
        plan = DiagramPlanBuilder().build_basic_flowchart(
            "A user submits a request. An analyst reviews it."
        )
        plan.style.chart_style = "soft_3d"
        out = MermaidRenderer().render(plan)
        assert "A(A user submits a request)" in out.content

    def test_true_3d_uses_stadium_node(self) -> None:
        plan = DiagramPlanBuilder().build_basic_flowchart(
            "A user submits a request. An analyst reviews it."
        )
        plan.style.chart_style = "true_3d"
        out = MermaidRenderer().render(plan)
        assert "A([A user submits a request])" in out.content
