"""Recipe action tests."""


from semantic_visual_builder.data.data_profiler import ColumnProfile, DatasetProfile
from semantic_visual_builder.planning.clarification import ClarificationOption, ClarificationRequest, PendingClarification
from semantic_visual_builder.planning.visual_plan import get_role
from semantic_visual_builder.planning.visual_plan_schema import DataRole, VisualPlan
from semantic_visual_builder.recipes.recipe_builder import RecipeBuilder
from semantic_visual_builder.recipes.recipe_store import RecipeStore
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


def _profile() -> DatasetProfile:
    return DatasetProfile(
        row_count=10,
        column_count=2,
        columns=[
            ColumnProfile("Region", "object", "categorical", 0, 0.0, 3, ["Gauteng"]),
            ColumnProfile("Amount", "float64", "numeric", 0, 0.0, 10, ["1.0"]),
        ],
    )


def _plan() -> VisualPlan:
    return VisualPlan(
        visual_kind="chart",
        intent="compare_categories",
        chart_type="bar",
        data_roles=[
            DataRole(role="category", field="Region"),
            DataRole(role="measure", field="Amount", aggregation="sum"),
        ],
    )


def test_save_recipe_action_calls_recipe_store(monkeypatch, tmp_path) -> None:
    state = AppState()
    state.dataset_context.profile = _profile()
    state.current_visual_plan = _plan()
    state.current_validation_result = ValidationResult()
    app = SemanticVisualBuilderApp(state, build_ui=False)
    app.recipe_store = RecipeStore(tmp_path)
    monkeypatch.setattr("semantic_visual_builder.ui.tkinter_app.simpledialog.askstring", lambda *args, **kwargs: "Weekly Summary")

    message = app.save_recipe_action()

    assert "Recipe saved:" in message
    assert state.active_recipe_name == "Weekly Summary"
    assert list(tmp_path.glob("*.recipe.json"))


def test_load_recipe_action_records_active_recipe_and_compatibility(monkeypatch, tmp_path) -> None:
    state = AppState()
    state.dataset_context.profile = _profile()
    app = SemanticVisualBuilderApp(state, build_ui=False)
    app.recipe_store = RecipeStore(tmp_path)
    recipe = RecipeBuilder().build_from_current_plan("Monthly Summary", _plan(), state.dataset_context.profile)
    saved_path = app.recipe_store.save_recipe(recipe)
    monkeypatch.setattr("semantic_visual_builder.ui.tkinter_app.filedialog.askopenfilename", lambda **kwargs: str(saved_path))

    message = app.load_recipe_action()

    assert "Recipe loaded:" in message
    assert state.active_recipe_name == "Monthly Summary"
    assert state.active_recipe is not None
    assert state.recipe_compatibility_result is not None


def test_apply_recipe_action_creates_plan_and_marks_preview_stale(monkeypatch, tmp_path) -> None:
    state = AppState()
    state.dataset_context.profile = _profile()
    app = SemanticVisualBuilderApp(state, build_ui=False)
    app.recipe_store = RecipeStore(tmp_path)
    recipe = RecipeBuilder().build_from_current_plan("Monthly Summary", _plan(), state.dataset_context.profile)
    saved_path = app.recipe_store.save_recipe(recipe)
    monkeypatch.setattr("semantic_visual_builder.ui.tkinter_app.filedialog.askopenfilename", lambda **kwargs: str(saved_path))
    app.load_recipe_action()

    message = app.apply_recipe_action()

    assert "Recipe applied:" in message
    assert state.current_visual_plan is not None
    assert state.current_visual_plan.metadata.is_preview_stale is True


def test_pending_clarification_can_be_stored_and_displayed() -> None:
    state = AppState()
    app = SemanticVisualBuilderApp(state, build_ui=False)
    app.clarification_text = FakeText()
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
    app._update_clarification_view()
    assert "Which field should be used" in app.clarification_text.content
    assert "- Region" in app.clarification_text.content


def test_answering_clarification_updates_app_state(monkeypatch) -> None:
    from semantic_visual_builder.planning.clarification import ClarificationOption, ClarificationRequest, PendingClarification

    state = AppState()
    state.dataset_context.profile = _profile()
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

    message = app.answer_clarification_action()

    assert "I interpreted" in message
    assert state.pending_clarification is None
    assert state.current_visual_plan is not None
    assert get_role(state.current_visual_plan, "category").field == "Region"
