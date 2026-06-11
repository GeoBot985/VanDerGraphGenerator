"""Tests for the editable-elements tooltip content."""

from semantic_visual_builder.planning.visual_plan_schema import DataRole, VisualPlan
from semantic_visual_builder.state.app_state import AppState
from semantic_visual_builder.ui.tkinter_app import SemanticVisualBuilderApp


def test_editable_elements_tooltip_reflects_current_plan_state() -> None:
    state = AppState()
    plan = VisualPlan(
        visual_kind="chart",
        intent="compare_categories",
        chart_type="bar",
        data_roles=[
            DataRole(role="category", field="Region"),
            DataRole(role="measure", field="Amount", aggregation="sum"),
        ],
    )
    plan.render_target.renderer = "plotly"
    plan.style.title = "Sales by Region"
    plan.style.title_size = 32
    plan.style.background = "#333333"
    plan.style.plot_background = "#333333"
    plan.style.palette = {"primary": "#d3d3d3"}
    plan.style.labels = {"x": "Region", "y": "Amount"}
    state.current_visual_plan = plan

    app = SemanticVisualBuilderApp(state, build_ui=False)

    tooltip = app._editable_elements_tooltip_text()

    assert "Editable graph elements" in tooltip
    assert "Chart type: bar" in tooltip
    assert "Renderer: plotly" in tooltip
    assert "Title: Sales by Region" in tooltip
    assert "Title size: 32" in tooltip
    assert "Primary series colour: #d3d3d3" in tooltip
    assert "Background: #333333" in tooltip
    assert "Category field: Region" in tooltip
    assert "Measure field: Amount" in tooltip
    assert "Measure aggregation: sum" in tooltip
