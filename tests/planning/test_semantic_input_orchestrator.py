"""Semantic input orchestration tests."""

from semantic_visual_builder.data.data_profiler import ColumnProfile, DatasetProfile
from semantic_visual_builder.llm.llm_mapping_result import (
    LlmMappingResult,
    LlmVisualPlanDraft,
)
from semantic_visual_builder.planning.clarification_engine import ClarificationEngine
from semantic_visual_builder.planning.field_mapper import FieldMapper
from semantic_visual_builder.planning.intent_mapper import IntentMapper
from semantic_visual_builder.planning.message_classifier import MessageIntent
from semantic_visual_builder.planning.planning_orchestrator import PlanningOrchestrator
from semantic_visual_builder.planning.refinement_engine import RefinementEngine
from semantic_visual_builder.planning.refinement_orchestrator import (
    RefinementOrchestrator,
)
from semantic_visual_builder.planning.semantic_input_orchestrator import (
    SemanticInputOrchestrator,
)
from semantic_visual_builder.planning.visual_plan_schema import DataRole, VisualPlan
from semantic_visual_builder.state.app_state import AppState
from semantic_visual_builder.validation.capability_validator import CapabilityValidator
from semantic_visual_builder.validation.visual_plan_validator import VisualPlanValidator


class FakeMapper:
    def __init__(self, result):
        self.result = result
        self.calls = 0

    def map_to_draft(self, **kwargs):
        self.calls += 1
        return self.result


class FakeClassifier:
    def __init__(self, intent=MessageIntent.UNKNOWN):
        self.intent = intent
        self.calls = 0

    def classify(self, message: str, has_current_plan: bool = False):
        self.calls += 1
        return self.intent


def _profile() -> DatasetProfile:
    return DatasetProfile(
        row_count=10,
        column_count=2,
        columns=[
            ColumnProfile("Region", "object", "categorical", 0, 0.0, 4, ["Gauteng"]),
            ColumnProfile("Amount", "float64", "numeric", 0, 0.0, 10, ["1.0"]),
        ],
    )


def _state(selected_model: str | None = "gemma4:12b") -> AppState:
    state = AppState()
    state.dataset_context.profile = _profile()
    state.model_registry.selected_model = selected_model
    state.current_visual_plan = VisualPlan(
        visual_kind="chart",
        intent="compare_categories",
        chart_type="bar",
        data_roles=[
            DataRole(role="category", field="Region"),
            DataRole(role="measure", field="Amount", aggregation="sum"),
        ],
    )
    return state


def _semantic_orchestrator(
    fake_result, classifier=None
) -> tuple[SemanticInputOrchestrator, FakeMapper]:
    mapper = FakeMapper(fake_result)
    planning_orchestrator = PlanningOrchestrator(
        llm_mapper=mapper,
        deterministic_mapper=IntentMapper(),
        field_mapper=FieldMapper(),
        visual_plan_validator=VisualPlanValidator(),
        capability_validator=CapabilityValidator(),
    )
    refinement_orchestrator = RefinementOrchestrator(
        llm_mapper=mapper,
        deterministic_refinement_engine=RefinementEngine(),
        visual_plan_validator=VisualPlanValidator(),
        capability_validator=CapabilityValidator(),
        clarification_engine=ClarificationEngine(),
    )
    return (
        SemanticInputOrchestrator(
            planning_orchestrator=planning_orchestrator,
            refinement_orchestrator=refinement_orchestrator,
            message_classifier=classifier or FakeClassifier(),
        ),
        mapper,
    )


def test_natural_refinement_phrase_reaches_llm_first() -> None:
    state = _state()
    orchestrator, mapper = _semantic_orchestrator(
        LlmMappingResult(
            raw_response="{}",
            parsed_json={},
            draft=LlmVisualPlanDraft(
                visual_kind="chart",
                intent="compare_categories",
                chart_type="pie",
                roles={
                    "category": {"field": "Region"},
                    "measure": {"field": "Amount", "aggregation": "sum"},
                },
                renderer="plotly",
            ),
        )
    )

    result = orchestrator.process_message("turn this into a pie", state, use_llm=True)

    assert mapper.calls == 1
    assert result.action == "refinement_request"
    assert result.mapping_method == "llm"
    assert any(line == "LLM attempted: yes" for line in result.messages)
    assert any(line == "LLM success: yes" for line in result.messages)


def test_deterministic_fallback_still_works_without_selected_model() -> None:
    state = _state(selected_model=None)
    orchestrator, mapper = _semantic_orchestrator(
        LlmMappingResult(
            raw_response="",
            parsed_json=None,
            draft=None,
            errors=["offline"],
        )
    )

    result = orchestrator.process_message("turn this into a pie", state, use_llm=True)

    assert mapper.calls == 0
    assert result.action == "refinement_request"
    assert result.mapping_method == "deterministic"
    assert result.used_fallback is False
    assert any(line == "LLM attempted: no" for line in result.messages)


def test_failed_llm_output_falls_back_to_deterministic_mapping() -> None:
    state = _state()
    orchestrator, mapper = _semantic_orchestrator(
        LlmMappingResult(raw_response="", parsed_json=None, draft=None, errors=["boom"])
    )

    result = orchestrator.process_message("turn this into a pie", state, use_llm=True)

    assert mapper.calls == 1
    assert result.action == "refinement_request"
    assert result.mapping_method == "deterministic_fallback"
    assert result.used_fallback is True
    assert any(line == "LLM attempted: yes" for line in result.messages)
    assert any(line == "LLM success: no" for line in result.messages)
