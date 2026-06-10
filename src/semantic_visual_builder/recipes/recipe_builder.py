"""Build recipe skeletons from visual plans."""

from __future__ import annotations

from datetime import datetime, timezone

from semantic_visual_builder.data.data_profiler import DatasetProfile
from semantic_visual_builder.planning.visual_plan import get_role, visual_plan_to_dict
from semantic_visual_builder.planning.visual_plan_schema import VisualPlan

from .recipe_schema import RecipeFieldExpectation, VisualRecipe


class RecipeBuilder:
    """Build a reusable recipe from the current plan."""

    schema_version = "1.0"

    def build_from_current_plan(
        self,
        recipe_name: str,
        visual_plan: VisualPlan,
        dataset_profile: DatasetProfile | None,
        description: str | None = None,
    ) -> VisualRecipe:
        expected_fields: list[RecipeFieldExpectation] = []
        profile_lookup = {column.name: column.semantic_type for column in dataset_profile.columns} if dataset_profile else {}
        for role in visual_plan.data_roles:
            if not role.field:
                continue
            expected_fields.append(
                RecipeFieldExpectation(
                    role=role.role,
                    field_name=role.field,
                    semantic_type=profile_lookup.get(role.field),
                    required=True,
                )
            )
        return VisualRecipe(
            recipe_name=recipe_name,
            schema_version=self.schema_version,
            visual_plan=visual_plan_to_dict(visual_plan),
            expected_fields=expected_fields,
            renderer=visual_plan.render_target.renderer,
            description=description,
            created_at=datetime.now(timezone.utc).isoformat(),
        )
