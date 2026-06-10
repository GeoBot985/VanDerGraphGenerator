"""Apply neutral style intents to Mermaid code."""

from __future__ import annotations

from semantic_visual_builder.planning.visual_plan_schema import VisualPlan


class MermaidStyleAdapter:
    def apply_style_to_mermaid(self, mermaid_code: str, visual_plan: VisualPlan) -> str:
        style = visual_plan.style
        direction = style.diagram_direction or (
            "LR" if style.orientation == "horizontal" else "TD"
        )
        lines = mermaid_code.splitlines()
        if lines and lines[0].startswith("flowchart"):
            lines[0] = f"flowchart {direction}"

        class_defs: list[str] = []
        class_defs_map = (
            style.palette.get("class_defs", {})
            if isinstance(style.palette, dict)
            else {}
        )
        if isinstance(class_defs_map, dict):
            for name, attrs in class_defs_map.items():
                if not isinstance(attrs, dict):
                    continue
                fill = attrs.get("fill") or "#ffffff"
                stroke = attrs.get("stroke") or "#1f4e79"
                color = attrs.get("color") or "#000000"
                class_defs.append(
                    "classDef "
                    f"{name} fill:{fill},"
                    f"stroke:{stroke},color:{color};"
                )

        if not class_defs:
            palette = style.palette if isinstance(style.palette, dict) else {}
            defaults = {
                "process": {
                    "fill": palette.get("primary") or style.background or "#d9eaf7",
                    "stroke": palette.get("secondary") or "#1f4e79",
                },
                "decision": {
                    "fill": palette.get("accent") or style.background or "#fff2cc",
                    "stroke": palette.get("primary") or "#1f4e79",
                },
                "start": {
                    "fill": palette.get("neutral") or "#e2f0d9",
                    "stroke": palette.get("primary") or "#1f4e79",
                },
                "end": {
                    "fill": palette.get("danger") or "#fce4d6",
                    "stroke": palette.get("primary") or "#1f4e79",
                },
            }
            for name, attrs in defaults.items():
                class_defs.append(
                    "classDef "
                    f"{name} fill:{attrs['fill']},"
                    f"stroke:{attrs['stroke']},color:#000000;"
                )

        node_fill = (
            style.palette.get("node_fill") if isinstance(style.palette, dict) else None
        ) or (style.background or "#d9eaf7")
        node_stroke = (
            (
                style.palette.get("node_stroke")
                if isinstance(style.palette, dict)
                else None
            )
            or (
                style.palette.get("primary")
                if isinstance(style.palette, dict)
                else None
            )
            or "#1f4e79"
        )
        if node_fill and node_stroke:
            class_defs.append(
                "classDef "
                f"plan_node fill:{node_fill},stroke:{node_stroke},color:#000000;"
            )

        return "\n".join(lines + [""] + class_defs)
