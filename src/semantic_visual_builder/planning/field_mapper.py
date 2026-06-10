"""Field mapping helpers for visual plans."""

from __future__ import annotations

from semantic_visual_builder.data.data_profiler import DatasetProfile

from .visual_plan import clone_visual_plan
from .visual_plan_schema import DataRole, VisualPlan


class FieldMapper:
    """Propose plan roles using a deterministic dataset profile lookup."""

    def propose_roles(self, message: str, dataset_profile: DatasetProfile, plan: VisualPlan) -> VisualPlan:
        text = message.lower()
        updated = clone_visual_plan(plan)

        datetime_fields = [column.name for column in dataset_profile.columns if column.semantic_type == "datetime"]
        numeric_fields = [column.name for column in dataset_profile.columns if column.semantic_type == "numeric"]
        categorical_fields = [column.name for column in dataset_profile.columns if column.semantic_type == "categorical"]

        def first_matching(names: list[str], candidate_words: tuple[str, ...]) -> str | None:
            for candidate in candidate_words:
                for name in names:
                    if candidate.lower() == name.lower():
                        return name
            return names[0] if names else None

        if updated.intent == "show_trend" or any(marker in text for marker in ("per week", "per month", "over time")):
            x_field = first_matching(datetime_fields, ("TransactionDate", "Date", "CreatedAt"))
            if x_field is None and dataset_profile.columns:
                x_field = dataset_profile.columns[0].name
            updated.data_roles = [
                DataRole(
                    role="x",
                    field=x_field,
                    transform="week" if "week" in text else "month" if "month" in text else None,
                )
            ]
            updated.data_roles.append(DataRole(role="y", field="row_count", aggregation="count"))
            return updated

        if "amount by region" in text:
            category = first_matching(categorical_fields, ("Region",))
            measure = first_matching(numeric_fields, ("Amount",))
            updated.data_roles = [
                DataRole(role="category", field=category),
                DataRole(role="measure", field=measure, aggregation="sum"),
            ]
            return updated

        if "transactions by region" in text:
            category = first_matching(categorical_fields, ("Region",))
            updated.data_roles = [
                DataRole(role="category", field=category),
                DataRole(role="measure", field="row_count", aggregation="count"),
            ]
            return updated

        if "transactions by status" in text:
            category = first_matching(categorical_fields, ("Status",))
            updated.data_roles = [
                DataRole(role="category", field=category),
                DataRole(role="measure", field="row_count", aggregation="count"),
            ]
            return updated

        if updated.intent == "compare_categories":
            category = categorical_fields[0] if categorical_fields else None
            measure = numeric_fields[0] if numeric_fields else "row_count"
            updated.data_roles = [
                DataRole(role="category", field=category),
                DataRole(role="measure", field=measure, aggregation="count" if measure == "row_count" else None),
            ]
            return updated

        if updated.intent == "show_relationship":
            x_field = numeric_fields[0] if numeric_fields else None
            y_field = numeric_fields[1] if len(numeric_fields) > 1 else numeric_fields[0] if numeric_fields else None
            updated.data_roles = [
                DataRole(role="x", field=x_field),
                DataRole(role="y", field=y_field),
            ]
            return updated

        return updated
