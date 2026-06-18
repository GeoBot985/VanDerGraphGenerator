"""Field mapping helpers for visual plans."""

from __future__ import annotations

import re

from semantic_visual_builder.data.data_profiler import DatasetProfile

from .visual_plan import clone_visual_plan, get_role
from .visual_plan_schema import DataRole, VisualPlan


class FieldMapper:
    """Propose plan roles using a deterministic dataset profile lookup."""

    def normalize_roles_for_chart_type(
        self, plan: VisualPlan, dataset_profile: DatasetProfile | None = None
    ) -> VisualPlan:
        updated = clone_visual_plan(plan)
        chart_type = updated.chart_type
        if chart_type is None:
            return updated

        category_role = get_role(updated, "category") or get_role(
            updated, "time_or_order"
        )
        measure_role = get_role(updated, "measure")
        x_role = get_role(updated, "x")
        y_role = get_role(updated, "y")

        if chart_type in {
            "bar",
            "horizontal_bar",
            "pie",
            "donut",
            "stacked_bar",
            "treemap",
            "waterfall",
            "funnel",
            "radar",
        }:
            category = category_role or x_role
            measure = measure_role or y_role
            roles: list[DataRole] = []
            if category is not None:
                roles.append(
                    DataRole(
                        role="category",
                        field=category.field,
                        transform=category.transform,
                        aggregation=category.aggregation,
                    )
                )
            if measure is not None:
                roles.append(
                    DataRole(
                        role="measure",
                        field=measure.field,
                        transform=measure.transform,
                        aggregation=measure.aggregation,
                    )
                )
            updated.data_roles = roles
            return updated

        if chart_type in {"line", "area"}:
            x = x_role or category_role
            y = y_role or measure_role
            if x is None and dataset_profile is not None:
                datetime_fields = [
                    column.name
                    for column in dataset_profile.columns
                    if column.semantic_type == "datetime"
                ]
                categorical_fields = [
                    column.name
                    for column in dataset_profile.columns
                    if column.semantic_type == "categorical"
                ]
                if datetime_fields:
                    x = DataRole(role="x", field=datetime_fields[0], transform="day")
                elif categorical_fields:
                    x = DataRole(role="x", field=categorical_fields[0])
            roles = []
            if x is not None:
                roles.append(
                    DataRole(
                        role="x",
                        field=x.field,
                        transform=x.transform,
                        aggregation=x.aggregation,
                    )
                )
            if y is not None:
                roles.append(
                    DataRole(
                        role="y",
                        field=y.field,
                        transform=y.transform,
                        aggregation=y.aggregation,
                    )
                )
            updated.data_roles = roles
            updated.intent = "show_trend"
            return updated

        if chart_type == "stacked_area":
            x = x_role or category_role
            stack_role = get_role(updated, "stack") or get_role(updated, "series")
            roles = []
            if x is not None:
                roles.append(
                    DataRole(
                        role="x",
                        field=x.field,
                        transform=x.transform,
                        aggregation=x.aggregation,
                    )
                )
            if stack_role is not None:
                roles.append(
                    DataRole(
                        role="stack",
                        field=stack_role.field,
                        transform=stack_role.transform,
                        aggregation=stack_role.aggregation,
                    )
                )
            if measure_role is not None:
                roles.append(
                    DataRole(
                        role="measure",
                        field=measure_role.field,
                        transform=measure_role.transform,
                        aggregation=measure_role.aggregation,
                    )
                )
            updated.data_roles = roles
            updated.intent = "show_trend"
            return updated

        if chart_type in {"scatter", "bubble"}:
            roles = []
            if x_role is not None:
                roles.append(
                    DataRole(
                        role="x",
                        field=x_role.field,
                        transform=x_role.transform,
                        aggregation=x_role.aggregation,
                    )
                )
            if y_role is not None:
                roles.append(
                    DataRole(
                        role="y",
                        field=y_role.field,
                        transform=y_role.transform,
                        aggregation=y_role.aggregation,
                    )
                )
            if chart_type == "bubble":
                size_role = get_role(updated, "size") or measure_role
                if size_role is not None:
                    roles.append(
                        DataRole(
                            role="size",
                            field=size_role.field,
                            transform=size_role.transform,
                            aggregation=size_role.aggregation,
                        )
                    )
            updated.data_roles = roles
            return updated

        if chart_type in {"gauge", "kpi_card"}:
            roles = []
            if measure_role is not None:
                roles.append(
                    DataRole(
                        role="measure",
                        field=measure_role.field,
                        transform=measure_role.transform,
                        aggregation=measure_role.aggregation,
                    )
                )
            updated.data_roles = roles
            updated.intent = "show_single_value"
            return updated

        return updated

    def complete_missing_roles(
        self,
        message: str,
        dataset_profile: DatasetProfile,
        plan: VisualPlan,
    ) -> VisualPlan:
        updated = self.normalize_roles_for_chart_type(plan, dataset_profile)
        proposed = self.propose_roles(message, dataset_profile, updated)
        proposed_roles = {role.role: role for role in proposed.data_roles}
        for index, role in enumerate(updated.data_roles):
            if role.field:
                continue
            proposal = proposed_roles.get(role.role)
            if proposal is None:
                continue
            if proposal.field is not None:
                updated.data_roles[index].field = proposal.field
            if updated.data_roles[index].transform is None:
                updated.data_roles[index].transform = proposal.transform
            if updated.data_roles[index].aggregation is None:
                updated.data_roles[index].aggregation = proposal.aggregation
        if not updated.data_roles and proposed.data_roles:
            updated.data_roles = proposed.data_roles
        return updated

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

        def set_time_series_measure(transform: str) -> VisualPlan:
            x_field = first_matching(datetime_fields, ("TransactionDate", "Date", "CreatedAt"))
            measure_field = first_matching(numeric_fields, ("Amount", "Value", "Price"))
            if x_field is None and datetime_fields:
                x_field = datetime_fields[0]
            elif x_field is None and dataset_profile.columns:
                x_field = dataset_profile.columns[0].name
            updated.data_roles = [
                DataRole(role="x", field=x_field, transform=transform),
                DataRole(
                    role="y",
                    field=measure_field or "row_count",
                    aggregation="sum" if measure_field else "count",
                ),
            ]
            return updated

        def add_filter(field: str, value: str) -> None:
            updated.filters.append({"field": field, "operator": "equals", "value": value})

        def extract_phrase(marker: str) -> str | None:
            match = re.search(rf"{re.escape(marker)}\s+([A-Za-z0-9_\- ]+)", text)
            if match:
                return match.group(1).strip().rstrip(".,")
            return None

        # --- Histogram ---
        if updated.chart_type == "gauge" or "gauge" in text:
            measure = first_matching(numeric_fields, ("Amount", "Value", "Score"))
            updated.chart_type = "gauge"
            updated.intent = "show_single_value"
            updated.render_target.renderer = "plotly"
            updated.data_roles = [
                DataRole(
                    role="measure",
                    field=measure or "row_count",
                    aggregation="sum" if measure else "count",
                )
            ]
            return updated

        if updated.chart_type == "kpi_card" or "kpi card" in text or "kpi" in text:
            measure = first_matching(numeric_fields, ("Amount", "Value", "Score"))
            updated.chart_type = "kpi_card"
            updated.intent = "show_single_value"
            updated.render_target.renderer = "plotly"
            updated.data_roles = [
                DataRole(
                    role="measure",
                    field=measure or "row_count",
                    aggregation="sum" if measure else "count",
                )
            ]
            return updated

        if updated.chart_type == "histogram" or "distribution of" in text or "histogram" in text:
            value_field: str | None = None
            for word in text.split():
                for col in numeric_fields:
                    if word == col.lower() or word == col.lower().replace(" ", "_"):
                        value_field = col
                        break
            if value_field is None:
                value_field = first_matching(numeric_fields, ("Amount", "Value", "Price"))
            if value_field:
                updated.chart_type = "histogram"
                updated.data_roles = [DataRole(role="value", field=value_field)]
                updated.render_target.renderer = "plotly"
            return updated

        if updated.chart_type == "bubble" or "bubble" in text:
            x_field = numeric_fields[0] if numeric_fields else None
            y_field = numeric_fields[1] if len(numeric_fields) > 1 else x_field
            size_field = numeric_fields[2] if len(numeric_fields) > 2 else x_field
            updated.chart_type = "bubble"
            updated.render_target.renderer = "plotly"
            updated.data_roles = [
                DataRole(role="x", field=x_field),
                DataRole(role="y", field=y_field),
                DataRole(role="size", field=size_field),
            ]
            return updated

        # --- Box plot ---
        if updated.chart_type == "box_plot" or "box plot" in text or "spread of" in text:
            value_field = first_matching(numeric_fields, ("Amount", "Value", "Price"))
            category_field = first_matching(categorical_fields, ("Region", "Status", "Category"))
            updated.chart_type = "box_plot"
            updated.render_target.renderer = "plotly"
            roles = [DataRole(role="value", field=value_field)]
            if category_field:
                roles.append(DataRole(role="category", field=category_field))
            updated.data_roles = roles
            return updated

        if updated.chart_type == "treemap" or "treemap" in text:
            category = first_matching(categorical_fields, ("Region", "Status", "Category"))
            measure = first_matching(numeric_fields, ("Amount", "Value"))
            updated.chart_type = "treemap"
            updated.intent = "show_matrix"
            updated.render_target.renderer = "plotly"
            updated.data_roles = [
                DataRole(role="category", field=category),
                DataRole(
                    role="measure",
                    field=measure or "row_count",
                    aggregation="sum" if measure else "count",
                ),
            ]
            return updated

        # --- Heatmap ---
        if updated.chart_type == "heatmap" or "heatmap" in text:
            x_cat = first_matching(categorical_fields, ("Status", "Category", "Type"))
            y_cat = first_matching(
                [f for f in categorical_fields if f != x_cat],
                ("Region", "Area", "Location"),
            )
            measure = first_matching(numeric_fields, ("Amount", "Value", "Count"))
            updated.chart_type = "heatmap"
            updated.render_target.renderer = "plotly"
            updated.data_roles = [
                DataRole(role="x_category", field=x_cat),
                DataRole(role="y_category", field=y_cat),
                DataRole(role="measure", field=measure or "row_count", aggregation="sum" if measure else "count"),
            ]
            return updated

        # --- Stacked bar ---
        if updated.chart_type == "stacked_bar" or "stacked" in text or "split by" in text:
            category = first_matching(categorical_fields, ("Region", "Area", "Category"))
            stack_candidates = [f for f in categorical_fields if f != category]
            stack = first_matching(stack_candidates, ("Status", "Type", "Group"))
            measure = first_matching(numeric_fields, ("Amount", "Value"))
            updated.chart_type = "stacked_bar"
            updated.render_target.renderer = "plotly"
            updated.data_roles = [
                DataRole(role="category", field=category),
                DataRole(role="stack", field=stack),
                DataRole(role="measure", field=measure or "row_count", aggregation="sum" if measure else "count"),
            ]
            return updated

        if updated.chart_type == "stacked_area" or "stacked area" in text:
            x_field = first_matching(datetime_fields, ("TransactionDate", "Date", "CreatedAt"))
            stack = first_matching(categorical_fields, ("Status", "Type", "Group"))
            measure = first_matching(numeric_fields, ("Amount", "Value"))
            updated.chart_type = "stacked_area"
            updated.intent = "show_trend"
            updated.render_target.renderer = "plotly"
            updated.data_roles = [
                DataRole(role="x", field=x_field or (dataset_profile.columns[0].name if dataset_profile.columns else None), transform="day"),
                DataRole(role="stack", field=stack),
                DataRole(role="measure", field=measure or "row_count", aggregation="sum" if measure else "count"),
            ]
            return updated

        if updated.chart_type == "area" or "area chart" in text:
            updated.chart_type = "area"
            updated.intent = "show_trend"
            updated.render_target.renderer = "plotly"
            return set_time_series_measure("day")

        if updated.chart_type in {"waterfall", "funnel", "radar", "donut"} or any(
            marker in text for marker in ("waterfall", "funnel", "radar", "donut")
        ):
            if "waterfall" in text or updated.chart_type == "waterfall":
                updated.chart_type = "waterfall"
            elif "funnel" in text or updated.chart_type == "funnel":
                updated.chart_type = "funnel"
            elif "radar" in text or updated.chart_type == "radar":
                updated.chart_type = "radar"
            else:
                updated.chart_type = "donut"
            updated.render_target.renderer = "plotly"
            return set_category_measure(
                first_matching(categorical_fields, ("Region", "Status", "Category")),
                first_matching(numeric_fields, ("Amount", "Value")) or "row_count",
                "sum" if numeric_fields else "count",
            )

        # --- Existing patterns ---
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
            existing_category = get_role(updated, "category")
            existing_measure = get_role(updated, "measure")
            category = existing_category.field if existing_category and existing_category.field else (
                categorical_fields[0] if categorical_fields else None
            )
            measure = existing_measure.field if existing_measure and existing_measure.field else (
                numeric_fields[0] if numeric_fields else "row_count"
            )
            # Preserve an aggregation inferred upstream (e.g. "sum of amount per region").
            aggregation = existing_measure.aggregation if existing_measure and existing_measure.aggregation else (
                "count" if measure == "row_count" else None
            )
            updated.data_roles = [
                DataRole(role="category", field=category),
                DataRole(role="measure", field=measure, aggregation=aggregation),
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
