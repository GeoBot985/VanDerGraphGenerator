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


class FakeSemanticResult:
    def __init__(self, plan: VisualPlan):
        self.action = "refinement_request"
        self.visual_plan = plan
        self.validation_result = ValidationResult()
        self.mapping_method = "deterministic_fallback"
        self.llm_mapping_result = None
        self.used_fallback = True
        self.messages = []
        self.clarification_requests = []


class FakeSemanticOrchestrator:
    def __init__(self, result: FakeSemanticResult):
        self.result = result
        self.calls = 0

    def handle_message(self, content, app_state, use_llm=True):
        _ = content, app_state, use_llm
        self.calls += 1
        return self.result


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


def test_new_request_does_not_get_treated_as_clarification_answer() -> None:
    state = AppState()
    state.current_visual_plan = _plan()
    state.current_validation_result = ValidationResult()
    state.set_pending_clarification(
        PendingClarification(
            request=ClarificationRequest(
                question="Which field should be used for the category axis?",
                reason="The category field is missing or ambiguous.",
                field_name="category",
                options=[ClarificationOption(label="Region", value="Region")],
            )
        )
    )
    updated_plan = VisualPlan(
        visual_kind="chart",
        intent="show_trend",
        chart_type="line",
        data_roles=[
            DataRole(role="x", field="Region"),
            DataRole(role="y", field="Amount", aggregation="sum"),
        ],
    )
    updated_plan.render_target.renderer = "plotly"
    app = SemanticVisualBuilderApp(state, build_ui=False)
    app.semantic_input_orchestrator = FakeSemanticOrchestrator(
        FakeSemanticResult(updated_plan)
    )
    app._chat_var = FakeVar("please change graph to line")
    app._use_llm_var = FakeVar(True)
    app._model_var = FakeVar("")
    app._append_chat = lambda content: None
    app._append_assistant_response = lambda content: None
    app._refresh_all_views = lambda: None
    app._update_clarification_view = lambda: None

    app.send_chat()

    assert state.pending_clarification is None
    assert app.semantic_input_orchestrator.calls == 1
    assert state.current_visual_plan is not None
    assert state.current_visual_plan.chart_type == "line"
