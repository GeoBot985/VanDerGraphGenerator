"""Plotly 3D / flat / soft-3D scene helpers.

This module owns the small piece of the renderer that decides how to translate
the neutral ``chart_style`` knob ("flat" | "soft_3d" | "true_3d") plus its
depth/bevel/perspective/lighting/shadow/tilt fields into Plotly trace and
layout shapes. Keeping it in one place keeps the individual chart builders
free of branching logic, and lets the deterministic validators assert against
the same model.
"""

from __future__ import annotations

from typing import Any

from semantic_visual_builder.planning.visual_plan_schema import StyleIntent, VisualPlan


def chart_style(plan: VisualPlan) -> str:
    """Return the active chart style for a plan, defaulting to ``flat``."""
    value = plan.style.chart_style
    if value in {"flat", "soft_3d", "true_3d"}:
        return value
    return "flat"


def is_3d_plan(plan: VisualPlan) -> bool:
    """True when the plan is rendered with any kind of 3D treatment."""
    return chart_style(plan) != "flat"


def depth(plan: VisualPlan, default: int = 12) -> int:
    value = plan.style.depth
    if value is None:
        return default if chart_style(plan) != "flat" else 0
    return max(0, min(200, value))


def bevel(plan: VisualPlan, default: int = 4) -> int:
    value = plan.style.bevel
    if value is None:
        return default if chart_style(plan) != "flat" else 0
    return max(0, value)


def perspective(plan: VisualPlan, default: float = 0.6) -> float:
    value = plan.style.perspective
    if value is None:
        return default if chart_style(plan) == "true_3d" else 0.1
    return max(0.0, min(1.0, float(value)))


def tilt(plan: VisualPlan, default: int = 25) -> int:
    value = plan.style.tilt
    if value is None:
        return default if chart_style(plan) == "true_3d" else 0
    return max(-180, min(180, int(value)))


def lighting(plan: VisualPlan, default: str = "soft") -> str:
    value = plan.style.lighting
    if value is None:
        return default if chart_style(plan) != "flat" else "flat"
    return value if value in {"flat", "soft", "dramatic"} else "soft"


def shadow(plan: VisualPlan) -> bool:
    if plan.style.shadow is None:
        return chart_style(plan) != "flat"
    return bool(plan.style.shadow)


def extrusion_marker(plan: VisualPlan, color: str | None = None) -> dict[str, Any]:
    """Return a Plotly marker dict that gives a bar/pie/exploded trace depth.

    Plotly draws the depth itself when ``marker.line`` is set and
    ``marker.pattern`` is provided; the truest depth effect comes from the
    separate scene helper below, but the marker style is what callers in the
    legacy flat trace builders use.
    """
    style = chart_style(plan)
    if style == "flat":
        return {}
    marker: dict[str, Any] = {
        "line": {"width": max(0, depth(plan, default=8) // 6)},
        "opacity": 0.95 if shadow(plan) else 1.0,
        "fill-opacity": 0.92 if style == "soft_3d" else 0.96,
    }
    if color is not None:
        marker["color"] = color
    return marker


def scene(plan: VisualPlan) -> dict[str, Any]:
    """Build a Plotly ``scene`` dict for true_3d charts."""
    style = chart_style(plan)
    if style != "true_3d":
        return {}
    light = lighting(plan, default="soft")
    light_colours = {
        "flat": (1.0, 1.0, 1.0),
        "soft": (0.85, 0.92, 1.0),
        "dramatic": (0.4, 0.45, 0.55),
    }
    rgba = light_colours.get(light, light_colours["soft"])
    return {
        "bgcolor": "rgba(0,0,0,0)",
        "xaxis": {"showbackground": True, "backgroundcolor": "rgba(0,0,0,0)"},
        "yaxis": {"showbackground": True, "backgroundcolor": "rgba(0,0,0,0)"},
        "zaxis": {"showbackground": True, "backgroundcolor": "rgba(0,0,0,0)"},
        "camera": {
            "eye": {
                "x": -perspective(plan) - 0.7,
                "y": -perspective(plan) - 0.7,
                "z": perspective(plan) + 0.6,
            },
            "up": {"x": 0, "y": 0, "z": 1},
            "center": {"x": 0, "y": 0, "z": 0},
        },
        "aspectmode": "auto",
        "dragmode": "orbit",
        "lighting": {
            "ambient": rgba,
            "diffuse": 0.7 if light == "soft" else 0.9,
            "specular": 0.4 if light == "soft" else 0.8,
            "roughness": 0.6 if light == "soft" else 0.3,
        },
    }


def bar3d_trace(plan: VisualPlan, x: list[Any], y: list[float], *, name: str = "Series",
                colorway: list[str] | None = None) -> dict[str, Any]:
    """Return a Plotly bar3d trace that respects the plan's 3D treatment."""
    style = chart_style(plan)
    if style == "true_3d":
        n = len(x)
        # Plotly bar3d draws each bar from a base z up to z+dz. We send the
        # value as the bar's *height* (dz) and place every bar on z=0 with a
        # category index on the y axis so the categories line up like a
        # city-skyline scene rather than flat ribbons on the floor.
        colors = colorway or [plan.style.palette.get("primary", "#4C78A8")] * n
        if colorway is None and isinstance(plan.style.palette, dict):
            sequence = plan.style.palette.get("sequence")
            if isinstance(sequence, list) and sequence:
                colors = [sequence[i % len(sequence)] for i in range(n)]
        return {
            "type": "bar3d",
            "x": list(x),
            "y": list(range(n)),
            "z": [0] * n,
            "dz": [float(v) for v in y],
            "name": name,
            "opacity": 0.95 if shadow(plan) else 1.0,
            "lighting": {
                "diffuse": 0.7 if lighting(plan) != "dramatic" else 0.9,
                "specular": 0.4 if lighting(plan) != "dramatic" else 0.8,
                "roughness": 0.6,
            },
            "marker": {
                "color": colors,
                "line": {"width": 0},
            },
        }
    # soft_3d and flat both fall back to a regular bar trace here.
    return {
        "type": "bar",
        "x": list(x),
        "y": list(y),
        "name": name,
    }


def surface3d_trace(plan: VisualPlan, x: list[Any], y: list[float], *, name: str = "Series") -> dict[str, Any]:
    """Return a Plotly mesh3d / scatter3d / surface trace for true_3d line charts."""
    style = chart_style(plan)
    if style != "true_3d":
        return {
            "type": "scatter",
            "mode": "lines+markers",
            "x": list(x),
            "y": list(y),
            "name": name,
        }
    primary = plan.style.palette.get("primary") if isinstance(plan.style.palette, dict) else None
    return {
        "type": "scatter3d",
        "mode": "lines+markers",
        "x": list(range(len(x))),
        "y": list(y),
        "z": [0] * len(x),
        "name": name,
        "line": {"color": primary or "#4C78A8", "width": 6 if lighting(plan) == "dramatic" else 4},
        "marker": {"color": primary or "#4C78A8", "size": 4},
    }


def pie3d_trace(plan: VisualPlan, labels: list[str], values: list[float], *,
                hole: float = 0.0, name: str = "Series") -> dict[str, Any]:
    """Return a Plotly pie trace with optional pull/explode for soft_3d."""
    style = chart_style(plan)
    trace: dict[str, Any] = {
        "type": "pie",
        "labels": labels,
        "values": values,
        "name": name,
    }
    if hole > 0:
        trace["hole"] = hole
    if style == "soft_3d":
        # Slight pull on every wedge produces a "raised" look without 3D math.
        n = len(labels)
        trace["pull"] = [0.05] * n
    return trace


def apply_3d_to_layout(plan: VisualPlan, layout: dict[str, Any]) -> dict[str, Any]:
    """Merge the plan's 3D scene settings into a Plotly layout dict."""
    if chart_style(plan) == "true_3d":
        layout.setdefault("scene", scene(plan))
    return layout


def describe(style: StyleIntent) -> str:
    """Human-readable description of a 3D treatment, used by validators."""
    value = style.chart_style or "flat"
    bits = [f"chart_style={value}"]
    if style.depth is not None:
        bits.append(f"depth={style.depth}")
    if style.bevel is not None:
        bits.append(f"bevel={style.bevel}")
    if style.perspective is not None:
        bits.append(f"perspective={style.perspective}")
    if style.tilt is not None:
        bits.append(f"tilt={style.tilt}")
    if style.lighting is not None:
        bits.append(f"lighting={style.lighting}")
    if style.shadow is not None:
        bits.append(f"shadow={style.shadow}")
    return ", ".join(bits)
