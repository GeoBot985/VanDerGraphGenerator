"""Tests for chat-based refinement routing in RefinementOrchestrator."""

from __future__ import annotations

from semantic_visual_builder.data.data_profiler import ColumnProfile, DatasetProfile
from semantic_visual_builder.llm.llm_mapping_result import (
    LlmMappingResult,
    LlmVisualPlanDraft,
)
from semantic_visual_builder.llm.ollama_client import OllamaModel
from semantic_visual_builder.planning.clarification_engine import ClarificationEngine
from semantic_visual_builder.planning.refinement_engine import RefinementEngine
from semantic_visual_builder.planning.refinement_orchestrator import (
    RefinementOrchestrator,
)
from semantic_visual_builder.planning.visual_plan_schema import DataRole, VisualPlan
from semantic_visual_builder.state.app_state import AppState
from semantic_visual_builder.state.conversation_state import ConversationMessage
from semantic_visual_builder.validation.capability_validator import CapabilityValidator
from semantic_visual_builder.validation.visual_plan_validator import VisualPlanValidator


class RecordingMapper:
    """Records which mapping method the orchestrator called."""

    def __init__(self, result: LlmMappingResult) -> None:
        self.result = result
        self.last_call: str | None = None
        self.last_history: list[dict[str, str]] | None = None

    def map_to_draft(self, **kwargs):
        self.last_call = "generate"
        return self.result

    def map_to_draft_with_history(self, **kwargs):
        self.last_call = "chat"
        self.last_history = kwargs.get("conversation_messages")
        return self.result


def _profile() -> DatasetProfile:
    return DatasetProfile(
        row_count=12,
        column_count=3,
        columns=[
            ColumnProfile("Region", "object", "categorical", 0, 0.0, 4, ["Gauteng"]),
            ColumnProfile("Amount", "float64", "numeric", 0, 0.0, 12, ["1.0"]),
        ],
    )


def _state() -> AppState:
    state = AppState()
    state.dataset_context.profile = _profile()
    state.model_registry.set_models([OllamaModel(name="mock-model")])
    return state


def _plan() -> VisualPlan:
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
    return plan


def _orchestrator(mapper: RecordingMapper) -> RefinementOrchestrator:
    return RefinementOrchestrator(
        llm_mapper=mapper,
        deterministic_refinement_engine=RefinementEngine(),
        visual_plan_validator=VisualPlanValidator(),
        capability_validator=CapabilityValidator(),
        clarification_engine=ClarificationEngine(),
    )


def _ok_result() -> LlmMappingResult:
    return LlmMappingResult(
        raw_response="{}",
        parsed_json={},
        draft=LlmVisualPlanDraft(
            visual_kind="chart",
            intent="compare_categories",
            chart_type="bar",
            roles={"category": {"field": "Region"}, "measure": {"field": "Amount"}},
        ),
        errors=[],
    )


def test_refinement_uses_chat_when_history_present() -> None:
    mapper = RecordingMapper(_ok_result())
    state = _state()
    state.conversation_state.messages = [
        ConversationMessage(role="user", content="Show sales by region"),
        ConversationMessage(role="assistant", content="Here is a bar chart."),
        ConversationMessage(role="user", content="Make it a line chart"),
    ]
    _orchestrator(mapper).refine_plan(
        current_plan=_plan(),
        user_message="Make it a line chart",
        app_state=state,
        use_llm=True,
    )
    assert mapper.last_call == "chat"
    # The current (last) message is excluded from history passed to chat.
    assert mapper.last_history is not None
    assert len(mapper.last_history) == 2
    assert mapper.last_history[0]["role"] == "user"
    assert mapper.last_history[1]["role"] == "assistant"


def test_refinement_falls_back_to_generate_without_history() -> None:
    mapper = RecordingMapper(_ok_result())
    state = _state()
    _orchestrator(mapper).refine_plan(
        current_plan=_plan(),
        user_message="Make it a line chart",
        app_state=state,
        use_llm=True,
    )
    assert mapper.last_call == "generate"


def test_refinement_falls_back_to_generate_when_mapper_lacks_chat() -> None:
    class GenerateOnlyMapper(RecordingMapper):
        def map_to_draft_with_history(self, **kwargs):  # noqa: D401
            raise AssertionError("chat path should not be used")

    # Override: remove the chat method so hasattr returns False.
    mapper = RecordingMapper(_ok_result())
    del type(mapper).map_to_draft_with_history
    state = _state()
    state.conversation_state.messages = [
        ConversationMessage(role="user", content="previous request"),
        ConversationMessage(role="user", content="Make it a line chart"),
    ]
    _orchestrator(mapper).refine_plan(
        current_plan=_plan(),
        user_message="Make it a line chart",
        app_state=state,
        use_llm=True,
    )
    assert mapper.last_call == "generate"
