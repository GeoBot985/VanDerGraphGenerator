"""Deterministic fallback planning mapper."""

from __future__ import annotations

from semantic_visual_builder.data.data_profiler import DatasetProfile
from semantic_visual_builder.knowledge.graph_matrix import GraphMatrix

from .diagram_plan_builder import DiagramPlanBuilder
from .field_mapper import FieldMapper
from .visual_plan import set_role
from .visual_plan_schema import VisualPlan


class DeterministicFallbackMapper:
    """Convert user text into a neutral visual plan draft as fallback."""

    def extract_explicit_chart_type(self, message: str) -> str | None:
        """Return chart_type only if the user message contains an explicit keyword, else None."""
        result = self.map_request_to_plan(message)
        return result.chart_type

    def map_request_to_plan(
        self,
        message: str,
        dataset_profile: DatasetProfile | None = None,
        graph_matrix: GraphMatrix | None = None,
    ) -> VisualPlan:
        text = message.lower()
        self._aggregation_roles = None
        intent = "unknown"
        visual_kind = "chart"
        chart_type: str | None = None
        diagram_type: str | None = None
        renderer: str | None = None

        if "swimlane" in text:
            intent = "show_process"
            visual_kind = "diagram"
            diagram_type = "swimlane"
            renderer = "mermaid"
        elif "timeline" in text:
            intent = "show_process"
            visual_kind = "diagram"
            diagram_type = "timeline"
            renderer = "mermaid"
        elif "network diagram" in text or "network graph" in text:
            intent = "show_process"
            visual_kind = "diagram"
            diagram_type = "network_diagram"
            renderer = "mermaid"
        elif "erd" in text or "entity relationship" in text:
            intent = "show_process"
            visual_kind = "diagram"
            diagram_type = "erd"
            renderer = "mermaid"
        elif "sequence diagram" in text:
            intent = "show_process"
            visual_kind = "diagram"
            diagram_type = "sequence_diagram"
            renderer = "mermaid"
        elif any(marker in text for marker in ("flowchart", "process")):
            intent = "show_process"
            visual_kind = "diagram"
            diagram_type = "flowchart"
            renderer = "mermaid"
        elif "gauge" in text:
            intent = "show_single_value"
            chart_type = "gauge"
            renderer = "plotly"
        elif "kpi card" in text or "kpi" in text:
            intent = "show_single_value"
            chart_type = "kpi_card"
            renderer = "plotly"
        elif "treemap" in text:
            intent = "show_matrix"
            chart_type = "treemap"
            renderer = "plotly"
        elif "waterfall" in text:
            intent = "compare_categories"
            chart_type = "waterfall"
            renderer = "plotly"
        elif "funnel" in text:
            intent = "compare_categories"
            chart_type = "funnel"
            renderer = "plotly"
        elif "bubble" in text:
            intent = "show_relationship"
            chart_type = "bubble"
            renderer = "plotly"
        elif "stacked area" in text:
            intent = "show_trend"
            chart_type = "stacked_area"
            renderer = "plotly"
        elif "area" in text:
            intent = "show_trend"
            chart_type = "area"
            renderer = "plotly"
        elif "pie" in text:
            intent = "compare_categories"
            chart_type = "pie"
            renderer = "plotly"
        elif "donut" in text:
            intent = "compare_categories"
            chart_type = "donut"
            renderer = "plotly"
        elif "radar" in text:
            intent = "compare_categories"
            chart_type = "radar"
            renderer = "plotly"
        elif "heatmap" in text or (
            "by" in text and "and" in text and "heatmap" in text
        ):
            intent = "show_matrix"
            chart_type = "heatmap"
            renderer = "plotly"
        elif "stacked" in text or "split by" in text:
            intent = "compare_stacked_categories"
            chart_type = "stacked_bar"
            renderer = "plotly"
        elif any(
            marker in text
            for marker in ("distribution of", "histogram", "spread of", "box plot")
        ):
            if "box plot" in text or "spread of" in text:
                intent = "show_distribution"
                chart_type = "box_plot"
            else:
                intent = "show_distribution"
                chart_type = "histogram"
            renderer = "plotly"
        elif "relationship between" in text or "scatter" in text:
            intent = "show_relationship"
            chart_type = "scatter"
            renderer = "plotly"
        elif any(marker in text for marker in ("per week", "per month", "over time")):
            intent = "show_trend"
            chart_type = "line"
            renderer = "plotly"
        elif any(marker in text for marker in ("by region", "by status", "compare")):
            intent = "compare_categories"
            chart_type = "bar"
            renderer = "plotly"

        # General aggregation requests such as "sum of amount per region" or
        # "average amount by status" that did not hit an explicit keyword above.
        if (
            chart_type is None
            and intent == "unknown"
            and dataset_profile is not None
        ):
            inferred = self._infer_aggregation_request(text, dataset_profile)
            if inferred is not None:
                (
                    intent,
                    chart_type,
                    renderer,
                    category_field,
                    measure_field,
                    aggregation,
                ) = inferred
                self._aggregation_roles = (category_field, measure_field, aggregation)

        plan = VisualPlan(
            visual_kind=visual_kind,
            intent=intent,
            chart_type=chart_type,
            diagram_type=diagram_type,
        )
        plan.render_target.renderer = renderer

        
        chart_style_hint = self.detect_chart_style(message)
        if chart_style_hint is not None:
            plan.style.chart_style = chart_style_hint
            plan.notes.append(f"3D treatment requested by user: {chart_style_hint}.")

        if intent == "show_process":
            plan = DiagramPlanBuilder().build_basic_flowchart(message)
            if diagram_type is not None:
                plan.diagram_type = diagram_type
            plan.render_target.renderer = "mermaid"

        if dataset_profile is not None:
            plan = FieldMapper().propose_roles(message, dataset_profile, plan)

        if (
            intent == "show_trend"
            and dataset_profile is not None
            and not plan.data_roles
        ):
            set_role(
                plan,
                "x",
                dataset_profile.columns[0].name if dataset_profile.columns else None,
            )
            set_role(plan, "y", "row_count", aggregation="count")

        if intent == "compare_categories" and dataset_profile is not None:
            if "amount by region" in text:
                set_role(plan, "category", "Region")
                set_role(plan, "measure", "Amount", aggregation="sum")
            elif "transactions by region" in text:
                set_role(plan, "category", "Region")
                set_role(plan, "measure", "row_count", aggregation="count")
            elif getattr(self, "_aggregation_roles", None) is not None:
                category_field, measure_field, aggregation = self._aggregation_roles
                if category_field is not None:
                    set_role(plan, "category", category_field)
                if measure_field is not None:
                    set_role(plan, "measure", measure_field, aggregation=aggregation)

        if graph_matrix is not None and plan.render_target.renderer is None:
            if plan.intent in graph_matrix.list_intents():
                plan.render_target.renderer = (
                    "plotly" if plan.visual_kind == "chart" else "mermaid"
                )

        if intent == "unknown":
            plan.notes.append("Intent could not be classified deterministically.")

        self._aggregation_roles = None
        return plan

    _AGGREGATION_KEYWORDS = (
        ("sum", "sum"), ("total", "sum"), ("avg", "avg"), ("average", "avg"),
        ("mean", "avg"), ("count", "count"), ("number of", "count"),
        ("min", "min"), ("minimum", "min"), ("max", "max"), ("maximum", "max"),
    )

    _GROUPING_PATTERNS = (
        r"\bper\s+(.+)",
        r"\bby\s+(.+)",
        r"\bfor\s+each\s+(.+)",
        r"\bgrouped\s+by\s+(.+)",
        r"\bbroken\s+down\s+by\s+(.+)",
        r"\bacross\s+(.+)",
        r"\bover\s+(.+)",
    )

    def _infer_aggregation_request(
        self, text: str, dataset_profile: DatasetProfile
    ) -> tuple[str, str, str, str | None, str | None, str] | None:
        """Detect aggregation-over-categorical requests without an explicit chart keyword.

        Returns (intent, chart_type, renderer, category_field, measure_field,
        aggregation) or None when no aggregation/grouping is recognisable.
        """
        import re

        lowered = text.lower()
        aggregation = None
        measure_phrase = lowered
        for keyword, agg in self._AGGREGATION_KEYWORDS:
            marker = f"{keyword} of "
            if marker in lowered:
                aggregation = agg
                measure_phrase = lowered.split(marker, 1)[1]
                break
            if lowered.startswith(keyword + " "):
                aggregation = agg
                measure_phrase = lowered[len(keyword) + 1:]
                break
        # "sum of transaction amounts" -> "transaction amounts" remains.
        if aggregation is None and (" of " in lowered or " per " in lowered or " by " in lowered):
            aggregation = "sum"  # default aggregation verb when grouping is present

        group_match = None
        for pattern in self._GROUPING_PATTERNS:
            match = re.search(pattern, lowered)
            if match:
                group_match = match.group(1)
                break
        if group_match is None and aggregation is None:
            return None

        def _column_matches(phrase: str, semantic_types: tuple[str, ...]) -> str | None:
            phrase = phrase.strip()
            if not phrase:
                return None
            words = set(re.findall(r"[a-z_]+", phrase))
            for column in dataset_profile.columns:
                if column.semantic_type not in semantic_types:
                    continue
                col_key = column.name.lower().replace(" ", "_")
                if col_key in words or any(word and word in col_key for word in words):
                    return column.name
            return None

        categorical_fields = [
            c for c in dataset_profile.columns if c.semantic_type == "categorical"
        ]
        numeric_fields = [
            c for c in dataset_profile.columns if c.semantic_type == "numeric"
        ]
        datetime_fields = [
            c for c in dataset_profile.columns if c.semantic_type == "datetime"
        ]

        category_field = _column_matches(group_match or "", ("categorical",)) if group_match else None
        if category_field is None and categorical_fields:
            category_field = categorical_fields[0].name

        # Measure: match a numeric column name inside the measure phrase.
        measure_field = _column_matches(measure_phrase, ("numeric",))
        if measure_field is None and numeric_fields:
            measure_field = numeric_fields[0].name
        if measure_field is None:
            # No numeric column -> count rows instead.
            measure_field = "row_count"
            aggregation = "count"

        # Time-series when the grouping target is a datetime field.
        time_field = _column_matches(group_match or "", ("datetime",))
        if time_field is not None or (
            group_match is None and datetime_fields and aggregation is not None
        ):
            return ("show_trend", "line", "plotly", time_field or (datetime_fields[0].name if datetime_fields else None), measure_field, aggregation)

        if category_field is None and group_match is not None:
            return None
        if category_field is None:
            return None

        return ("compare_categories", "bar", "plotly", category_field, measure_field, aggregation)


    #: Map of common phrases the user uses to ask for a 3D chart. Detected in
    #: addition to chart_type and intent so the same flat chart can be re-rendered
    #: as soft_3d / true_3d without changing the chart_type.
    _CHART_STYLE_KEYWORDS: tuple[tuple[str, str], ...] = (
        ("true 3d", "true_3d"),
        ("true3d", "true_3d"),
        ("3d scene", "true_3d"),
        ("immersive 3d", "true_3d"),
        ("fully 3d", "true_3d"),
        ("interactive 3d", "true_3d"),
        ("soft 3d", "soft_3d"),
        ("soft3d", "soft_3d"),
        ("extruded", "soft_3d"),
        ("raised", "soft_3d"),
        ("3d", "soft_3d"),
    )

    def detect_chart_style(self, message: str) -> str | None:
        """Return ``soft_3d`` / ``true_3d`` / ``flat`` from natural language.

        A request that mentions "true 3d" or "immersive 3d" upgrades to a full
        3D scene; a request that simply says "3d" stays at the cheaper
        ``soft_3d`` extrusion. ``None`` is returned when no 3D hint is
        present, leaving the chart style unset (the profile / default wins).
        """
        lowered = message.lower()
        # Order matters: more specific phrases first.
        for keyword, value in self._CHART_STYLE_KEYWORDS:
            if keyword in lowered:
                return value
        if "flat" in lowered and "3d" not in lowered:
            return "flat"
        return None