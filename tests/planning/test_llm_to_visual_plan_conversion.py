"""LLM draft to visual plan conversion tests."""

from semantic_visual_builder.llm.llm_mapping_result import LlmVisualPlanDraft
from semantic_visual_builder.planning.visual_plan import (
    summarize_visual_plan,
    visual_plan_from_llm_draft,
)


def test_llm_chart_draft_converts_to_visual_plan_roles() -> None:
    draft = LlmVisualPlanDraft(
        visual_kind="chart",
        intent="compare_categories",
        chart_type="bar",
        roles={
            "category": {"field": "Region"},
            "measure": {"field": "Amount", "aggregation": "sum"},
        },
        style={"title": "Total Amount by Region", "colour_scheme": "blue", "highlights": {}},
        renderer="plotly",
    )
    plan = visual_plan_from_llm_draft(draft)
    assert plan.visual_kind == "chart"
    assert plan.chart_type == "bar"
    assert plan.render_target.renderer == "plotly"
    assert plan.style.title == "Total Amount by Region"
    assert {role.role for role in plan.data_roles} == {"category", "measure"}


def test_llm_flowchart_draft_converts_to_diagram_plan() -> None:
    draft = LlmVisualPlanDraft(
        visual_kind="diagram",
        intent="show_process",
        diagram_type="flowchart",
        roles={},
        style={"title": "Process Flow"},
        renderer="mermaid",
    )
    plan = visual_plan_from_llm_draft(draft)
    assert plan.visual_kind == "diagram"
    assert plan.diagram_type == "flowchart"
    assert plan.render_target.renderer == "mermaid"


def test_style_title_converts_correctly() -> None:
    draft = LlmVisualPlanDraft(visual_kind="chart", intent="compare_categories", chart_type="bar", roles={}, style={"title": "Test"})
    plan = visual_plan_from_llm_draft(draft)
    assert plan.style.title == "Test"


def test_renderer_converts_to_render_target() -> None:
    draft = LlmVisualPlanDraft(visual_kind="chart", intent="compare_categories", chart_type="bar", roles={}, renderer="plotly")
    plan = visual_plan_from_llm_draft(draft)
    assert plan.render_target.renderer == "plotly"


def test_summary_includes_background_fields() -> None:
    draft = LlmVisualPlanDraft(
        visual_kind="chart",
        intent="compare_categories",
        chart_type="bar",
        roles={"category": {"field": "Region"}, "measure": {"field": "Amount", "aggregation": "sum"}},
        style={"background": "#90ee90", "plot_background": "#90ee90"},
        renderer="plotly",
    )
    plan = visual_plan_from_llm_draft(draft)

    summary = summarize_visual_plan(plan)

    assert "Background: #90ee90" in summary
    assert "Plot background: #90ee90" in summary


def test_structured_background_object_is_normalised_to_hex_string() -> None:
    draft = LlmVisualPlanDraft(
        visual_kind="chart",
        intent="compare_categories",
        chart_type="bar",
        roles={
            "category": {"field": "Region"},
            "measure": {"field": "Amount", "aggregation": "sum"},
        },
        style={
            "background": {"type": "solid", "color": "#e6ffe6"},
            "plot_background": {"type": "solid", "color": "#e6ffe6"},
        },
        renderer="plotly",
    )

    plan = visual_plan_from_llm_draft(draft)

    assert plan.style.background == "#e6ffe6"
    assert plan.style.plot_background == "#e6ffe6"


def test_llm_title_size_converts_to_visual_plan() -> None:
    draft = LlmVisualPlanDraft(
        visual_kind="chart",
        intent="compare_categories",
        chart_type="bar",
        roles={"category": {"field": "Region"}, "measure": {"field": "Amount", "aggregation": "sum"}},
        style={"title": "Bollocks Chart", "title_size": 32},
        renderer="plotly",
    )

    plan = visual_plan_from_llm_draft(draft)

    assert plan.style.title == "Bollocks Chart"
    assert plan.style.title_size == 32
    assert "Title size: 32" in summarize_visual_plan(plan)
