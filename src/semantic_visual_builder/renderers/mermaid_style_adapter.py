"""Apply style intents to Mermaid code, with extracted palette support."""

from __future__ import annotations

from semantic_visual_builder.planning.visual_plan_schema import VisualPlan


def _safe_hex(value: str | None, fallback: str) -> str:
    """Return value if it looks like a valid hex colour, else fallback."""
    if not value:
        return fallback
    text = value.lstrip("#")
    if len(text) in (3, 6) and all(c in "0123456789abcdefABCDEF" for c in text):
        return value
    return fallback


def _text_colour_for_bg(bg: str | None) -> str:
    """Guess readable text colour for a given background hex."""
    if not bg:
        return "#000000"
    text = bg.lstrip("#")
    if len(text) == 3:
        text = "".join(c * 2 for c in text)
    if len(text) != 6:
        return "#000000"
    r, g, b = int(text[0:2], 16), int(text[2:4], 16), int(text[4:6], 16)
    brightness = (r * 299 + g * 587 + b * 114) / 1000
    return "#ffffff" if brightness < 128 else "#000000"


def _build_init_directive(style: object) -> str | None:
    """Return a Mermaid %%{init}%% directive when theme variables need setting."""
    theme_vars: dict[str, str] = {}
    font_family = getattr(style, "font_family", None)
    label_size = getattr(style, "label_size", None) or getattr(style, "tick_size", None)
    if font_family:
        theme_vars["fontFamily"] = font_family
    if label_size:
        theme_vars["fontSize"] = f"{label_size}px"
    if not theme_vars:
        return None
    pairs = ", ".join(f'"{k}": "{v}"' for k, v in theme_vars.items())
    return "%%{init: {'theme': 'base', 'themeVariables': {" + pairs + "}}}%%"


class MermaidStyleAdapter:
    def apply_style_to_mermaid(self, mermaid_code: str, visual_plan: VisualPlan) -> str:
        style = visual_plan.style
        direction = style.diagram_direction or (
            "LR" if style.orientation == "horizontal" else "TD"
        )
        lines = mermaid_code.splitlines()
        if lines and lines[0].startswith("flowchart"):
            lines[0] = f"flowchart {direction}"

        init = _build_init_directive(style)
        if init:
            lines = [init] + lines

        palette = style.palette if isinstance(style.palette, dict) else {}
        background = style.background or "#ffffff"
        primary = _safe_hex(palette.get("primary") if isinstance(palette, dict) else None, "#d9eaf7")
        secondary = _safe_hex(palette.get("secondary") if isinstance(palette, dict) else None, "#1f4e79")
        accent = _safe_hex(palette.get("accent") if isinstance(palette, dict) else None, "#fff2cc")
        neutral = _safe_hex(palette.get("neutral") if isinstance(palette, dict) else None, "#e2f0d9")
        danger = _safe_hex(palette.get("danger") if isinstance(palette, dict) else None, "#fce4d6")

        border_radius = getattr(style, "border_radius", None)
        stroke_width = getattr(style, "stroke_width", None)

        def _class_def(name: str, fill: str, stroke: str, color: str) -> str:
            parts = [f"fill:{fill}", f"stroke:{stroke}", f"color:{color}"]
            if stroke_width is not None:
                parts.append(f"stroke-width:{stroke_width}px")
            if border_radius is not None:
                parts.append(f"rx:{border_radius}px")
            return f"classDef {name} {','.join(parts)};"

        class_defs: list[str] = []
        class_defs_map = (
            palette.get("class_defs", {}) if isinstance(palette, dict) else {}
        )
        if isinstance(class_defs_map, dict) and class_defs_map:
            for name, attrs in class_defs_map.items():
                if not isinstance(attrs, dict):
                    continue
                fill = _safe_hex(attrs.get("fill"), "#ffffff")
                stroke = _safe_hex(attrs.get("stroke"), "#1f4e79")
                color = _safe_hex(attrs.get("color"), _text_colour_for_bg(fill))
                class_defs.append(_class_def(name, fill, stroke, color))

        if not class_defs:
            node_fill_raw = (
                palette.get("node_fill") if isinstance(palette, dict) else None
            ) or background
            node_stroke_raw = (
                palette.get("node_stroke") if isinstance(palette, dict) else None
            ) or secondary
            node_fill = _safe_hex(node_fill_raw, primary)
            node_stroke = _safe_hex(node_stroke_raw, secondary)
            process_text = _text_colour_for_bg(node_fill)
            decision_text = _text_colour_for_bg(accent)
            start_text = _text_colour_for_bg(neutral)
            end_text = _text_colour_for_bg(danger)

            defaults = {
                "process": (node_fill, node_stroke, process_text),
                "decision": (accent, secondary, decision_text),
                "start": (neutral, secondary, start_text),
                "end": (danger, secondary, end_text),
            }
            for name, (fill, stroke, color) in defaults.items():
                class_defs.append(_class_def(name, fill, stroke, color))

        plan_node_fill = _safe_hex(
            palette.get("node_fill") if isinstance(palette, dict) else None,
            background,
        )
        plan_node_stroke = _safe_hex(
            (palette.get("node_stroke") or palette.get("primary"))
            if isinstance(palette, dict)
            else None,
            "#1f4e79",
        )
        plan_text = _text_colour_for_bg(plan_node_fill)
        class_defs.append(_class_def("plan_node", plan_node_fill, plan_node_stroke, plan_text))

        return "\n".join(lines + [""] + class_defs)
