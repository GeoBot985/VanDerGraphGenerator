"""Field mapping helpers for visual plans."""

from __future__ import annotations

import re

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

        def set_category_measure(category_name: str | None, measure_name: str | None, aggregation: str | None) -> VisualPlan:
            updated.data_roles = [
                DataRole(role="category", field=category_name),
                DataRole(role="measure", field=measure_name, aggregation=aggregation),
            ]
            return updated

        def set_time_series(transform: str) -> VisualPlan:
            x_field = first_matching(datetime_fields, ("TransactionDate", "Date", "CreatedAt"))
            if x_field is None and datetime_fields:
                x_field = datetime_fields[0]
            elif x_field is None and dataset_profile.columns:
                x_field = dataset_profile.columns[0].name
            updated.data_roles = [
                DataRole(role="x", field=x_field, transform=transform),
                DataRole(role="y", field="row_count", aggregation="count"),
            ]
            return updated

        def add_filter(field: str, value: str) -> None:
            updated.filters.append({"field": field, "operator": "equals", "value": value})

        def extract_phrase(marker: str) -> str | None:
            match = re.search(rf"{re.escape(marker)}\s+([A-Za-z0-9_\- ]+)", text)
            if match:
                return match.group(1).strip().rstrip(".,")
            return None

        if "average amount by status" in text:
            return set_category_measure(first_matching(categorical_fields, ("Status",)), first_matching(numeric_fields, ("Amount",)), "avg")

        if "approved amount by region" in text:
            region = first_matching(categorical_fields, ("Region",))
            amount = first_matching(numeric_fields, ("Amount",))
            add_filter("Status", "Approved")
            return set_category_measure(region, amount, "sum")

        if "amount by region" in text:
            return set_category_measure(first_matching(categorical_fields, ("Region",)), first_matching(numeric_fields, ("Amount",)), "sum")

        if "failed transactions per week" in text:
            add_filter("Status", "Failed")
            return set_time_series("week")

        if "per week" in text or "by week" in text:
            return set_time_series("week")

        if "per month" in text or "by month" in text:
            return set_time_series("month")

        if updated.intent == "show_trend" or "over time" in text:
            return set_time_series("day")

        if "transactions by region" in text:
            return set_category_measure(first_matching(categorical_fields, ("Region",)), "row_count", "count")

        if "transactions by status" in text:
            return set_category_measure(first_matching(categorical_fields, ("Status",)), "row_count", "count")

        if "transactions per week" in text:
            return set_time_series("week")

        if "show amount by category" in text:
            category = categorical_fields[0] if categorical_fields else None
            measure = first_matching(numeric_fields, ("Amount",))
            return set_category_measure(category, measure, "sum")

        if "highlight" in text:
            highlighted = extract_phrase("highlight")
            if highlighted:
                updated.style.highlights = {"value": highlighted}
                updated.notes.append(f"Highlight intent captured for {highlighted}.")

        if "blue" in text:
            updated.style.colour_scheme = "blue"
        if "corporate blue" in text:
            updated.style.colour_scheme = "corporate blue"
        if "horizontal" in text and updated.chart_type == "bar":
            updated.chart_type = "horizontal_bar"
            updated.style.orientation = "horizontal"
        elif "horizontal" in text:
            updated.style.orientation = "horizontal"

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
