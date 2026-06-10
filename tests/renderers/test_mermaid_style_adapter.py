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
