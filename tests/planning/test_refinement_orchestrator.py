"""Refinement orchestrator tests."""

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
from semantic_visual_builder.validation.capability_validator import CapabilityValidator
from semantic_visual_builder.validation.visual_plan_validator import VisualPlanValidator


class FakeMapper:
    def __init__(self, result: LlmMappingResult):
        self.result = result

    def map_to_draft(self, **kwargs):
        return self.result


def _profile() -> DatasetProfile:
    return DatasetProfile(
        row_count=12,
        column_count=3,
        columns=[
            ColumnProfile("Region", "object", "categorical", 0, 0.0, 4, ["Gauteng"]),
            ColumnProfile("Status", "object", "categorical", 0, 0.0, 3, ["Failed"]),
            ColumnProfile("Amount", "float64", "numeric", 0, 0.0, 12, ["1.0"]),
        ],
    )


def _state() -> AppState:
    state = AppState()
    state.dataset_context.profile = _profile()
    state.model_registry.set_models([OllamaModel(name="mock-model")])
    return state


def _orchestrator(result: LlmMappingResult) -> RefinementOrchestrator:
    return RefinementOrchestrator(
        llm_mapper=FakeMapper(result),
        deterministic_refinement_engine=RefinementEngine(),
        visual_plan_validator=VisualPlanValidator(),
        capability_validator=CapabilityValidator(),
        clarification_engine=ClarificationEngine(),
    )


def test_llm_refinement_preserves_existing_roles_when_only_chart_type_changes() -> None:
    current_plan = VisualPlan(
        visual_kind="chart",
        intent="compare_categories",
        chart_type="bar",
        data_roles=[
            DataRole(role="category", field="Region"),
            DataRole(role="measure", field="Amount", aggregation="sum"),
        ],
    )
    current_plan.render_target.renderer = "plotly"
    result = _orchestrator(
        LlmMappingResult(
            raw_response="{}",
            parsed_json={},
            draft=LlmVisualPlanDraft(
                visual_kind="chart",
                intent="compare_categories",
                chart_type="horizontal_bar",
                roles={},
                style={},
            ),
        )
    ).refine_plan(current_plan, "Make it horizontal", _state())
    assert result.visual_plan is not None
    assert result.visual_plan.chart_type == "horizontal_bar"
    assert {role.role: role.field for role in result.visual_plan.data_roles} == {
        "category": "Region",
        "measure": "Amount",
    }


def test_failed_llm_refinement_falls_back_to_deterministic_refinement() -> None:
    current_plan = VisualPlan(
        visual_kind="chart",
        intent="compare_categories",
        chart_type="bar",
        data_roles=[
            DataRole(role="category", field="Region"),
            DataRole(role="measure", field="Amount", aggregation="sum"),
        ],
    )
    current_plan.render_target.renderer = "plotly"
    result = _orchestrator(
        LlmMappingResult(raw_response="", parsed_json=None, draft=None, errors=["boom"])
    ).refine_plan(current_plan, "Make it horizontal", _state())
    assert result.used_fallback is True
    assert result.visual_plan is not None
    assert result.visual_plan.chart_type == "horizontal_bar"


def test_invalid_refined_plan_triggers_clarification() -> None:
    current_plan = VisualPlan(
        visual_kind="chart",
        intent="compare_categories",
        chart_type="bar",
        data_roles=[
            DataRole(role="category", field="Missing"),
            DataRole(role="measure", field="Amount", aggregation="sum"),
        ],
    )
    result = _orchestrator(
        LlmMappingResult(
            raw_response="{}",
            parsed_json={},
            draft=LlmVisualPlanDraft(
                visual_kind="chart",
                intent="compare_categories",
                chart_type="horizontal_bar",
                roles={},
                style={},
            ),
        )
    ).refine_plan(current_plan, "Make it horizontal", _state())
    assert result.visual_plan is None
    assert result.clarification_requests


def test_accepted_refinement_marks_preview_stale() -> None:
    current_plan = VisualPlan(
        visual_kind="chart",
        intent="compare_categories",
        chart_type="bar",
        data_roles=[
            DataRole(role="category", field="Region"),
            DataRole(role="measure", field="Amount", aggregation="sum"),
        ],
    )
    current_plan.render_target.renderer = "plotly"
    result = _orchestrator(
        LlmMappingResult(
            raw_response="{}",
            parsed_json={},
            draft=LlmVisualPlanDraft(
                visual_kind="chart",
                intent="compare_categories",
                chart_type="horizontal_bar",
                roles={},
                style={},
            ),
        )
    ).refine_plan(current_plan, "Make it horizontal", _state())
    assert result.visual_plan is not None
    assert result.visual_plan.metadata.is_preview_stale is True
