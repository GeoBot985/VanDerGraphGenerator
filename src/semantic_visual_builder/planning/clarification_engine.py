"""Detect and apply clarifying questions for visual plans."""

from __future__ import annotations

from typing import Iterable

from semantic_visual_builder.data.data_profiler import DatasetProfile
from semantic_visual_builder.knowledge.graph_matrix import GraphMatrix

from .clarification import ClarificationOption, ClarificationRequest
from .visual_plan import clone_visual_plan, get_role, set_role
from .visual_plan_schema import VisualPlan


class ClarificationEngine:
    """Identify missing or ambiguous plan inputs and apply answers."""

    def detect_needed_clarification(
        self,
        plan: VisualPlan,
        dataset_profile: DatasetProfile | None,
        graph_matrix: GraphMatrix | None = None,
    ) -> list[ClarificationRequest]:
        if dataset_profile is None:
            return []

        requests: list[ClarificationRequest] = []
        fields = {column.name: column for column in dataset_profile.columns}
        required_roles = (
            graph_matrix.required_roles_for(plan.chart_type)
            if graph_matrix is not None and plan.chart_type is not None
            else []
        )
        categorical = [
            column.name
            for column in dataset_profile.columns
            if column.semantic_type == "categorical"
        ]
        numeric = [
            column.name
            for column in dataset_profile.columns
            if column.semantic_type == "numeric"
        ]
        datetimes = [
            column.name
            for column in dataset_profile.columns
            if column.semantic_type == "datetime"
        ]

        def available_options(names: Iterable[str]) -> list[ClarificationOption]:
            return [ClarificationOption(label=name, value=name) for name in names]

        def add_request(
            question: str,
            reason: str,
            field_name: str | None,
            options: list[ClarificationOption],
        ) -> None:
            requests.append(
                ClarificationRequest(
                    question=question,
                    reason=reason,
                    field_name=field_name,
                    options=options,
                )
            )

        x_role = (
            get_role(plan, "x")
            or get_role(plan, "category")
            or get_role(plan, "time_or_order")
        )
        y_role = get_role(plan, "y") or get_role(plan, "measure")

        if (
            x_role
            and x_role.field
            and x_role.field not in fields
            and x_role.field != "row_count"
        ):
            add_request(
                question=(
                    f"I could not find a column named {x_role.field}. "
                    "Which field should be used?"
                ),
                reason=f"Requested field '{x_role.field}' does not exist.",
                field_name=x_role.role,
                options=available_options(categorical or datetimes or numeric),
            )

        if (
            y_role
            and y_role.field
            and y_role.field not in fields
            and y_role.field != "row_count"
        ):
            add_request(
                question=(
                    f"I could not find a column named {y_role.field}. "
                    "Which field should be used for the measure axis?"
                ),
                reason=f"Requested field '{y_role.field}' does not exist.",
                field_name=y_role.role,
                options=available_options(numeric or categorical),
            )

        if plan.visual_kind == "chart":
            if plan.chart_type in {"bar", "horizontal_bar", "pie"}:
                if x_role is None or not x_role.field:
                    if len(categorical) > 1 and len(numeric) > 1:
                        first_category = categorical[0]
                        first_measure = numeric[0]
                        second_category = categorical[1]
                        second_measure = numeric[1]
                        add_request(
                            question=(
                                "I found more than one likely mapping. "
                                f"Should I use {first_measure} by {first_category}, "
                                f"or {second_measure} by {second_category}?"
                            ),
                            reason="Both category and measure fields are ambiguous.",
                            field_name="category",
                            options=available_options(categorical),
                        )
                    elif len(categorical) > 1:
                        add_request(
                            question=(
                                "I need a category field for this chart's "
                                "category axis. "
                                f"Available category fields: {', '.join(categorical)}."
                            ),
                            reason="The category field is missing or ambiguous.",
                            field_name="category",
                            options=available_options(categorical),
                        )
                if y_role is None or not y_role.field:
                    measure_label = "measure"
                    if "value" in required_roles:
                        measure_label = "value"
                    numeric_fields_text = ", ".join(numeric)
                    if len(numeric) > 1:
                        add_request(
                            question=(
                                "I need to know which numeric field to use as the "
                                f"{measure_label}. Available numeric fields: "
                                f"{numeric_fields_text}."
                            ),
                            reason="The measure field is missing or ambiguous.",
                            field_name="measure",
                            options=available_options(numeric),
                        )
            if plan.chart_type == "line":
                if x_role is None or not x_role.field:
                    if len(datetimes) > 1:
                        add_request(
                            question=(
                                "Which date field should be used for the time axis? "
                                f"Available date fields: {', '.join(datetimes)}."
                            ),
                            reason="Multiple candidate date fields exist.",
                            field_name="x",
                            options=available_options(datetimes),
                        )
                if y_role is None or not y_role.field:
                    if len(numeric) > 1:
                        numeric_fields_text = ", ".join(numeric)
                        question_text = (
                            "Which numeric field should be used for the line "
                            f"values? Available numeric fields: {numeric_fields_text}."
                        )
                        add_request(
                            question=question_text,
                            reason="Multiple candidate numeric measures exist.",
                            field_name="y",
                            options=available_options(numeric),
                        )
            if plan.chart_type == "scatter":
                if x_role is None or not x_role.field or x_role.field not in numeric:
                    if len(numeric) > 1:
                        add_request(
                            question=(
                                "Which numeric field should be used for the x axis? "
                                f"Available numeric fields: {', '.join(numeric)}."
                            ),
                            reason="Scatter plots require a numeric x field.",
                            field_name="x",
                            options=available_options(numeric),
                        )
                if y_role is None or not y_role.field or y_role.field not in numeric:
                    if len(numeric) > 1:
                        add_request(
                            question=(
                                "Which numeric field should be used for the y axis? "
                                f"Available numeric fields: {', '.join(numeric)}."
                            ),
                            reason="Scatter plots require a numeric y field.",
                            field_name="y",
                            options=available_options(numeric),
                        )

            if plan.chart_type == "pie" and x_role and x_role.field in fields:
                category_profile = fields[x_role.field]
                if category_profile.unique_count > 6:
                    add_request(
                        question=(
                            f"{x_role.field} has {category_profile.unique_count} "
                            "categories. Continue with a pie chart?"
                        ),
                        reason="Pie charts are hard to read with many categories.",
                        field_name=x_role.role,
                        options=[
                            ClarificationOption(label="Continue", value="yes"),
                            ClarificationOption(
                                label="Choose another chart", value="no"
                            ),
                        ],
                    )

        return requests

    def apply_answer(
        self,
        plan: VisualPlan,
        clarification: ClarificationRequest,
        answer: str,
    ) -> VisualPlan:
        updated = clone_visual_plan(plan)
        answer_text = answer.strip()
        lowered = answer_text.lower()

        if clarification.options:
            selected = self._match_option(clarification.options, answer_text)
            if selected is not None:
                answer_text = selected.value
                lowered = selected.value.lower()

        if clarification.field_name in {"x", "category", "time_or_order"}:
            set_role(updated, clarification.field_name, answer_text)
        elif clarification.field_name in {"y", "measure"}:
            aggregation = "count" if answer_text == "row_count" else None
            set_role(
                updated,
                clarification.field_name,
                answer_text,
                aggregation=aggregation,
            )
        elif clarification.field_name and clarification.field_name not in {"x", "y"}:
            set_role(updated, clarification.field_name, answer_text)

        if clarification.reason.lower().startswith(
            "pie charts are hard to read"
        ) and lowered in {"yes", "continue"}:
            updated.notes.append("User confirmed the pie chart with many categories.")
        if "highlight" in clarification.question.lower():
            updated.style.highlights = {"value": answer_text}

        return updated

    def _match_option(
        self, options: list[ClarificationOption], answer: str
    ) -> ClarificationOption | None:
        lowered = answer.lower()
        for option in options:
            if option.label.lower() == lowered or option.value.lower() == lowered:
                return option
        return None
