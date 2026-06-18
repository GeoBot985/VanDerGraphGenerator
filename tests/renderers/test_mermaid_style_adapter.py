"""Mermaid style adapter tests."""

from semantic_visual_builder.planning.visual_plan_schema import VisualPlan
from semantic_visual_builder.renderers.mermaid_style_adapter import MermaidStyleAdapter


def test_mermaid_style_adapter_updates_direction_and_class_defs() -> None:
    plan = VisualPlan(visual_kind="diagram", intent="process")
    plan.style.diagram_direction = "LR"
    plan.style.background = "#ffffff"
    plan.style.palette = {
        "primary": "#1f4e79",
        "node_fill": "#d9eaf7",
        "node_stroke": "#1f4e79",
        "class_defs": {
            "process": {
                "fill": "#d9eaf7",
                "stroke": "#1f4e79",
                "color": "#000000",
            }
        },
    }

    result = MermaidStyleAdapter().apply_style_to_mermaid("flowchart TD\nA-->B", plan)

    assert result.startswith("flowchart LR")
    assert "classDef process fill:#d9eaf7,stroke:#1f4e79,color:#000000;" in result
    assert "classDef plan_node fill:#d9eaf7,stroke:#1f4e79,color:#000000;" in result


def test_mermaid_style_adapter_applies_border_radius_and_stroke_width() -> None:
    plan = VisualPlan(visual_kind="diagram", intent="process")
    plan.style.border_radius = 10
    plan.style.stroke_width = 2
    plan.style.background = "#ffffff"
    plan.style.palette = {"primary": "#1f4e79"}

    result = MermaidStyleAdapter().apply_style_to_mermaid("flowchart TD\nA-->B", plan)

    assert "stroke-width:2px" in result
    assert "rx:10px" in result


def test_mermaid_style_adapter_prepends_init_for_font_family() -> None:
    plan = VisualPlan(visual_kind="diagram", intent="process")
    plan.style.font_family = "Georgia"
    plan.style.background = "#ffffff"
    plan.style.palette = {}

    result = MermaidStyleAdapter().apply_style_to_mermaid("flowchart TD\nA-->B", plan)

    assert result.startswith("%%{init:")
    assert "Georgia" in result
    assert "flowchart TD" in result
