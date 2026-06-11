"""Apply structured patches to visual plans."""

from __future__ import annotations

from copy import deepcopy

from .visual_plan import clone_visual_plan, set_role
from .visual_plan_patch import VisualPlanPatch
from .visual_plan_schema import VisualPlan


class VisualPlanPatchApplier:
    """Apply a structured patch without parsing raw user text."""

    def apply_patch(self, base: VisualPlan, patch: VisualPlanPatch) -> VisualPlan:
        updated = clone_visual_plan(base)

        if patch.visual_kind is not None:
            updated.visual_kind = patch.visual_kind
        if patch.intent is not None:
            updated.intent = patch.intent
        if patch.chart_type is not None:
            updated.chart_type = patch.chart_type
        if patch.diagram_type is not None:
            updated.diagram_type = patch.diagram_type
        if patch.render_target is not None:
            if patch.render_target.renderer is not None:
                updated.render_target.renderer = patch.render_target.renderer
            if patch.render_target.output_format is not None:
                updated.render_target.output_format = patch.render_target.output_format

        if patch.data_roles is not None:
            for role in patch.data_roles:
                set_role(
                    updated, role.role, role.field, role.transform, role.aggregation
                )
        if patch.filters is not None:
            updated.filters = [deepcopy(item) for item in patch.filters]
        if patch.grouping is not None:
            updated.grouping = list(patch.grouping)
        if patch.diagram_nodes is not None:
            updated.diagram_nodes = deepcopy(patch.diagram_nodes)
        if patch.diagram_edges is not None:
            updated.diagram_edges = deepcopy(patch.diagram_edges)

        if patch.style is not None:
            if patch.style.title is not None:
                updated.style.title = patch.style.title
            if patch.style.subtitle is not None:
                updated.style.subtitle = patch.style.subtitle
            if patch.style.title_size is not None:
                updated.style.title_size = patch.style.title_size
            if patch.style.colour_scheme is not None:
                updated.style.colour_scheme = patch.style.colour_scheme
            if patch.style.palette:
                updated.style.palette = deepcopy(patch.style.palette)
            if patch.style.font_family is not None:
                updated.style.font_family = patch.style.font_family
            if patch.style.grid is not None:
                updated.style.grid = patch.style.grid
            if patch.style.legend_position is not None:
                updated.style.legend_position = patch.style.legend_position
            if patch.style.background is not None:
                updated.style.background = patch.style.background
            if patch.style.plot_background is not None:
                updated.style.plot_background = patch.style.plot_background
            if patch.style.diagram_direction is not None:
                updated.style.diagram_direction = patch.style.diagram_direction
            if patch.style.highlights:
                updated.style.highlights = deepcopy(patch.style.highlights)
            if patch.style.labels:
                updated.style.labels = deepcopy(patch.style.labels)
            if patch.style.orientation is not None:
                updated.style.orientation = patch.style.orientation

        if patch.notes is not None:
            for note in patch.notes:
                if note not in updated.notes:
                    updated.notes.append(note)

        return updated
