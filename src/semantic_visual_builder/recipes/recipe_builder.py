"""Build recipe skeletons from visual plans."""

from __future__ import annotations

from datetime import datetime, timezone

from semantic_visual_builder.data.data_profiler import DatasetProfile
from semantic_visual_builder.planning.visual_plan import (
    clone_visual_plan,
    visual_plan_to_dict,
)
from semantic_visual_builder.planning.visual_plan_schema import VisualPlan
from semantic_visual_builder.utils.text_sanitize import normalize_name
from semantic_visual_builder.version import APP_VERSION

from .recipe_schema import (
    RecipeFieldExpectation,
    RecipeMetadata,
    RecipeRenderer,
    RecipeStyle,
    VisualRecipe,
)


class RecipeBuilder:
    """Build a reusable recipe from the current plan."""

    schema_version = "2.0"

    def build_from_current_plan(
        self,
        recipe_name: str,
        visual_plan: VisualPlan,
        dataset_profile: DatasetProfile | None,
        description: str | None = None,
    ) -> VisualRecipe:
        expected_fields: list[RecipeFieldExpectation] = []
        profile_lookup = (
            {column.name: column.semantic_type for column in dataset_profile.columns}
            if dataset_profile
            else {}
        )
        plan_copy = clone_visual_plan(visual_plan)

        for role in plan_copy.data_roles:
            if not role.field:
                continue
            semantic_type = (
                "numeric"
                if role.field == "row_count"
                else profile_lookup.get(role.field)
            )
            expected_fields.append(
                RecipeFieldExpectation(
                    role=role.role,
                    field_name=role.field,
                    semantic_type=semantic_type,
                    required=True,
                    aliases=[],
                )
            )
            role.field = f"{{{{{role.role}}}}}"

        template = visual_plan_to_dict(plan_copy)
        metadata = RecipeMetadata(
            recipe_id=normalize_name(recipe_name) or "untitled_recipe",
            recipe_name=recipe_name,
            description=description,
            schema_version=self.schema_version,
            app_version_created=APP_VERSION,
            created_at=datetime.now(timezone.utc).isoformat(),
        )
        renderer = (
            RecipeRenderer(
                renderer=visual_plan.render_target.renderer or "",
                output_type=visual_plan.render_target.output_format,
            )
            if visual_plan.render_target.renderer
            else None
        )
        return VisualRecipe(
            metadata=metadata,
            expected_fields=expected_fields,
            visual_plan_template=template,
            style=RecipeStyle(
                title=visual_plan.style.title,
                subtitle=visual_plan.style.subtitle,
                colour_scheme=visual_plan.style.colour_scheme,
                highlights=dict(visual_plan.style.highlights),
                labels=dict(visual_plan.style.labels),
                orientation=visual_plan.style.orientation,
            ),
            renderer=renderer,
            notes=list(visual_plan.notes),
        )
