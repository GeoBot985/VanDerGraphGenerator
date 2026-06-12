"""Workflow display tests."""

from semantic_visual_builder.planning.visual_plan_schema import DataRole, StyleIntent, VisualPlan
from semantic_visual_builder.planning.workflow_state import WorkflowStep
from semantic_visual_builder.state.app_state import AppState
from semantic_visual_builder.state.revision_history import RevisionHistory
from semantic_visual_builder.ui.tkinter_app import SemanticVisualBuilderApp
from semantic_visual_builder.validation.validation_result import ValidationMessage, ValidationResult, ValidationSeverity


def test_workflow_display_helpers() -> None:
    state = AppState()
    state.workflow_state.advance_to(WorkflowStep.PLAN_READY)
    state.current_visual_plan = VisualPlan(
        visual_kind="chart",
        intent="show_trend",
        chart_type="line",
        data_roles=[DataRole(role="x", field="TransactionDate", transform="week"), DataRole(role="y", field="row_count", aggregation="count")],
        style=StyleIntent(title="Trend"),
    )
    state.current_validation_result = ValidationResult(messages=[ValidationMessage(ValidationSeverity.INFO, "Plan is valid.")])
    state.revision_history = RevisionHistory()
    state.revision_history.add_revision("Created", state.current_visual_plan)

    app = SemanticVisualBuilderApp(state, build_ui=False)
    assert app.workflow_step_text() == "Workflow step: plan_ready"
    assert "Visual kind: chart" in app.visual_plan_text()
    assert "Plan is valid." in app.validation_text_value()
    assert app.revision_count_text() == "Revision count: 1"
