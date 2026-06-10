"""Apply style profiles to visual plans."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field

from semantic_visual_builder.planning.visual_plan_schema import VisualPlan

from .style_schema import StyleProfile


@dataclass
class StyleApplicationResult:
    success: bool
    visual_plan: VisualPlan | None = None
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


class StyleApplier:
    def apply_style(
        self,
        visual_plan: VisualPlan,
        style_profile: StyleProfile,
    ) -> StyleApplicationResult:
        if visual_plan.visual_kind not in style_profile.supported_visual_kinds:
            return StyleApplicationResult(
                success=False,
                errors=[
                    f"Style '{style_profile.style_name}' does not support "
                    f"{visual_plan.visual_kind} visuals."
                ],
            )

        warnings: list[str] = []
        if style_profile.chart.background is not None:
            visual_plan.style.background = style_profile.chart.background
        if style_profile.chart.plot_background is not None:
            visual_plan.style.plot_background = style_profile.chart.plot_background
        if style_profile.chart.grid is not None:
            visual_plan.style.grid = style_profile.chart.grid
        if style_profile.chart.legend_position is not None:
            visual_plan.style.legend_position = style_profile.chart.legend_position
        if style_profile.diagram.direction is not None:
            visual_plan.style.diagram_direction = style_profile.diagram.direction
        if style_profile.typography.font_family is not None:
            visual_plan.style.font_family = style_profile.typography.font_family
        if style_profile.palette.sequence:
            visual_plan.style.palette = {
                f"sequence_{index}": colour
                for index, colour in enumerate(style_profile.palette.sequence)
            }
        if style_profile.palette.primary is not None:
            visual_plan.style.palette["primary"] = style_profile.palette.primary
        if style_profile.palette.secondary is not None:
            visual_plan.style.palette["secondary"] = style_profile.palette.secondary
        if style_profile.palette.accent is not None:
            visual_plan.style.palette["accent"] = style_profile.palette.accent
        if style_profile.palette.neutral is not None:
            visual_plan.style.palette["neutral"] = style_profile.palette.neutral
        if style_profile.palette.warning is not None:
            visual_plan.style.palette["warning"] = style_profile.palette.warning
        if style_profile.palette.success is not None:
            visual_plan.style.palette["success"] = style_profile.palette.success
        if style_profile.palette.danger is not None:
            visual_plan.style.palette["danger"] = style_profile.palette.danger
        if style_profile.diagram.node_fill is not None:
            visual_plan.style.palette["node_fill"] = style_profile.diagram.node_fill
        if style_profile.diagram.node_stroke is not None:
            visual_plan.style.palette["node_stroke"] = style_profile.diagram.node_stroke
        if style_profile.diagram.decision_fill is not None:
            visual_plan.style.palette["decision_fill"] = (
                style_profile.diagram.decision_fill
            )
        if style_profile.diagram.edge_colour is not None:
            visual_plan.style.palette["edge_colour"] = style_profile.diagram.edge_colour
        if style_profile.diagram.class_defs:
            visual_plan.style.palette["class_defs"] = deepcopy(
                style_profile.diagram.class_defs
            )

        if visual_plan.style.title is None and style_profile.metadata.style_name:
            visual_plan.style.title = style_profile.metadata.style_name

        visual_plan.metadata.style_profile_id = style_profile.style_id
        visual_plan.metadata.style_profile_name = style_profile.style_name
        visual_plan.metadata.is_preview_stale = True
        return StyleApplicationResult(
            success=True,
            visual_plan=visual_plan,
            warnings=warnings,
        )
