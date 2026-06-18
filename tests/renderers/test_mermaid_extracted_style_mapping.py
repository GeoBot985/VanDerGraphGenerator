"""Tests for Mermaid style adapter with extracted palette/style."""

from __future__ import annotations

from unittest.mock import MagicMock

from semantic_visual_builder.renderers.mermaid_style_adapter import MermaidStyleAdapter


def _make_plan(
    background: str | None = None,
    primary: str | None = None,
    secondary: str | None = None,
    accent: str | None = None,
    neutral: str | None = None,
    orientation: str | None = None,
    diagram_direction: str | None = None,
) -> MagicMock:
    plan = MagicMock()
    plan.style.background = background or "#ffffff"
    plan.style.orientation = orientation
    plan.style.diagram_direction = diagram_direction
    plan.style.palette = {
        "primary": primary,
        "secondary": secondary,
        "accent": accent,
        "neutral": neutral,
        "class_defs": {},
    }
    return plan


SIMPLE_FLOWCHART = "flowchart TD\n    A --> B"


class TestMermaidExtractedStyleMapping:
    def setup_method(self) -> None:
        self.adapter = MermaidStyleAdapter()

    def test_extracted_palette_creates_classdef_rules(self) -> None:
        plan = _make_plan(primary="#1f4e79", secondary="#5b9bd5")
        result = self.adapter.apply_style_to_mermaid(SIMPLE_FLOWCHART, plan)
        assert "classDef" in result

    def test_text_colour_applied_safely(self) -> None:
        plan = _make_plan(primary="#111111", background="#111111")
        result = self.adapter.apply_style_to_mermaid(SIMPLE_FLOWCHART, plan)
        assert "color:#ffffff" in result

    def test_mermaid_valid_with_partial_style(self) -> None:
        plan = _make_plan()
        result = self.adapter.apply_style_to_mermaid(SIMPLE_FLOWCHART, plan)
        assert "flowchart" in result
        assert "classDef" in result

    def test_plan_node_classdef_appended(self) -> None:
        plan = _make_plan(primary="#1f4e79")
        result = self.adapter.apply_style_to_mermaid(SIMPLE_FLOWCHART, plan)
        assert "plan_node" in result

    def test_direction_applied_to_flowchart_header(self) -> None:
        plan = _make_plan(diagram_direction="LR")
        result = self.adapter.apply_style_to_mermaid(SIMPLE_FLOWCHART, plan)
        assert "flowchart LR" in result

    def test_no_invalid_hex_in_output(self) -> None:
        plan = _make_plan()
        result = self.adapter.apply_style_to_mermaid(SIMPLE_FLOWCHART, plan)
        lines_with_fill = [line for line in result.splitlines() if "fill:" in line]
        for line in lines_with_fill:
            assert "fill:#" in line or "fill:rgba" in line

    def test_dark_node_gets_white_text(self) -> None:
        plan = _make_plan(primary="#111111", secondary="#222222", background="#111111")
        result = self.adapter.apply_style_to_mermaid(SIMPLE_FLOWCHART, plan)
        assert "color:#ffffff" in result
