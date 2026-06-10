"""Clarification display tests."""

from semantic_visual_builder.planning.clarification import ClarificationOption, ClarificationRequest, PendingClarification
from semantic_visual_builder.planning.visual_plan import get_role
from semantic_visual_builder.planning.visual_plan_schema import DataRole, VisualPlan
from semantic_visual_builder.state.app_state import AppState
from semantic_visual_builder.ui.tkinter_app import SemanticVisualBuilderApp
from semantic_visual_builder.validation.validation_result import ValidationResult


class FakeVar:
    def __init__(self, value: str):
        self.value = value

    def get(self):
        return self.value

    def set(self, value):
        self.value = value


class FakeText:
    def __init__(self):
        self.content = ""

    def configure(self, **kwargs):
        return None

    def delete(self, *args, **kwargs):
        self.content = ""

    def insert(self, index, content):
        self.content = content


def _plan() -> VisualPlan:
    return VisualPlan(
        visual_kind="chart",
        intent="compare_categories",
        chart_type="bar",
        data_roles=[DataRole(role="measure", field="Amount", aggregation="sum")],
    )


def test_pending_clarification_can_be_displayed() -> None:
    state = AppState()
    state.set_pending_clarification(
        PendingClarification(
            request=ClarificationRequest(
                question="Which field should be used for the category axis?",
                reason="The category field is missing or ambiguous.",
                field_name="category",
                options=[ClarificationOption(label="Region", value="Region"), ClarificationOption(label="Status", value="Status")],
            )
        )
    )
    app = SemanticVisualBuilderApp(state, build_ui=False)
    app.clarification_text = FakeText()

    app._update_clarification_view()

    assert "Which field should be used" in app.clarification_text.content


def test_answering_clarification_updates_app_state() -> None:
    state = AppState()
    state.current_visual_plan = _plan()
    state.current_validation_result = ValidationResult()
    state.set_pending_clarification(
        PendingClarification(
            request=ClarificationRequest(
                question="Which field should be used for the category axis?",
                reason="The category field is missing or ambiguous.",
                field_name="category",
                options=[ClarificationOption(label="Region", value="Region"), ClarificationOption(label="Status", value="Status")],
            )
        )
    )
    app = SemanticVisualBuilderApp(state, build_ui=False)
    app.clarification_text = FakeText()
    app._clarification_answer_var = FakeVar("Region")

    app.answer_clarification_action()

    assert state.pending_clarification is None
    assert state.current_visual_plan is not None
    assert get_role(state.current_visual_plan, "category").field == "Region"
