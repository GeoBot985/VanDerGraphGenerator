"""End-to-end semantic flow tests."""

from __future__ import annotations

from pathlib import Path

from semantic_visual_builder.data.csv_loader import CsvLoader
from semantic_visual_builder.data.data_profiler import DataProfiler
from semantic_visual_builder.knowledge.graph_matrix import GraphMatrixLoader
from semantic_visual_builder.llm.llm_mapping_result import (
    LlmMappingResult,
    LlmVisualPlanDraft,
)
from semantic_visual_builder.planning.clarification_engine import ClarificationEngine
from semantic_visual_builder.planning.deterministic_fallback_mapper import (
    DeterministicFallbackMapper,
)
from semantic_visual_builder.planning.deterministic_fallback_patch_planner import (
    DeterministicFallbackPatchPlanner,
)
from semantic_visual_builder.planning.field_mapper import FieldMapper
from semantic_visual_builder.planning.planning_orchestrator import PlanningOrchestrator
from semantic_visual_builder.planning.refinement_orchestrator import (
    RefinementOrchestrator,
)
from semantic_visual_builder.planning.semantic_input_orchestrator import (
    SemanticInputOrchestrator,
)
from semantic_visual_builder.planning.visual_plan_patch_applier import (
    VisualPlanPatchApplier,
)
from semantic_visual_builder.state.app_state import AppState
from semantic_visual_builder.validation.capability_validator import CapabilityValidator
from semantic_visual_builder.validation.visual_plan_validator import VisualPlanValidator


class FakeMapper:
    def __init__(self, result: LlmMappingResult):
        self.result = result
        self.calls = 0

    def map_to_draft(self, **kwargs):
        self.calls += 1
        return self.result


def _profile(path: str):
    root = Path(__file__).resolve().parents[2]
    loaded = CsvLoader().load(root / path)
    return DataProfiler().profile(loaded.dataframe)


def _state(profile_path: str = "assets/samples/sample_transactions.csv") -> AppState:
    state = AppState()
    state.dataset_context.profile = _profile(profile_path)
    root = Path(__file__).resolve().parents[2]
    state.graph_matrix = GraphMatrixLoader(
        root / "graph_matrix" / "graph_matrix.json"
    ).load()
    state.model_registry.selected_model = "gemma4:12b"
    return state


def _orchestrator(
    result: LlmMappingResult,
) -> tuple[SemanticInputOrchestrator, FakeMapper]:
    mapper = FakeMapper(result)
    planning_orchestrator = PlanningOrchestrator(
        llm_mapper=mapper,
        deterministic_mapper=DeterministicFallbackMapper(),
        field_mapper=FieldMapper(),
        visual_plan_validator=VisualPlanValidator(),
        capability_validator=CapabilityValidator(),
    )
    refinement_orchestrator = RefinementOrchestrator(
        llm_mapper=mapper,
        deterministic_fallback_patch_planner=DeterministicFallbackPatchPlanner(),
        patch_applier=VisualPlanPatchApplier(),
        visual_plan_validator=VisualPlanValidator(),
        capability_validator=CapabilityValidator(),
        clarification_engine=ClarificationEngine(),
    )
    return (
        SemanticInputOrchestrator(
            planning_orchestrator=planning_orchestrator,
            refinement_orchestrator=refinement_orchestrator,
        ),
        mapper,
    )


def test_create_bar_chart_then_refine_to_pie_updates_trace_and_plan() -> None:
    state = _state()
    orchestrator, mapper = _orchestrator(
        LlmMappingResult(
            raw_response="{}",
            parsed_json={},
            draft=LlmVisualPlanDraft(
                visual_kind="chart",
                intent="compare_categories",
                action="create_plan",
                chart_type="bar",
                roles={
                    "category": {"field": "Region"},
                    "measure": {"field": "Amount", "aggregation": "sum"},
                },
                renderer="plotly",
            ),
        )
    )

    create_result = orchestrator.handle_message(
        "Show total amount by region as a bar chart.", state, use_llm=True
    )
    assert mapper.calls == 1
    assert create_result.trace is not None
    assert create_result.trace.mapping_method == "llm"
    assert create_result.trace.used_fallback is False
    assert create_result.trace.validation_success is True
    assert create_result.visual_plan is not None
    state.set_visual_plan(create_result.visual_plan)

    refine_orchestrator, refine_mapper = _orchestrator(
        LlmMappingResult(
            raw_response="{}",
            parsed_json={},
            draft=LlmVisualPlanDraft(
                visual_kind="chart",
                intent="compare_categories",
                action="refine_plan",
                chart_type="pie",
                roles={},
                renderer="plotly",
            ),
        )
    )
    state.current_visual_plan = create_result.visual_plan
    refine_result = refine_orchestrator.handle_message(
        "turn this into a pie", state, use_llm=True
    )
    assert refine_mapper.calls == 1
    assert refine_result.trace is not None
    assert refine_result.trace.mapping_method.startswith("llm")
    assert refine_result.trace.used_fallback is False
    assert refine_result.visual_plan is not None
    state.set_visual_plan(refine_result.visual_plan)
    assert state.current_visual_plan.chart_type == "pie"
    assert state.current_visual_plan.metadata.is_preview_stale is True


def test_histogram_flow_uses_llm_and_plotly() -> None:
    state = _state("assets/samples/sample_transactions.csv")
    orchestrator, mapper = _orchestrator(
        LlmMappingResult(
            raw_response="{}",
            parsed_json={},
            draft=LlmVisualPlanDraft(
                visual_kind="chart",
                intent="show_distribution",
                action="create_plan",
                chart_type="histogram",
                roles={"value": {"field": "Amount"}},
                renderer="plotly",
            ),
        )
    )

    result = orchestrator.handle_message(
        "show the distribution of age", state, use_llm=True
    )
    assert mapper.calls == 1
    assert result.trace is not None
    assert result.trace.llm_success is True
    assert result.visual_plan is not None
    assert result.visual_plan.chart_type == "histogram"
    assert result.visual_plan.render_target.renderer == "plotly"
    state.set_visual_plan(result.visual_plan)
    assert state.current_visual_plan.metadata.is_preview_stale is True


def test_unsupported_donut_chart_is_rejected_by_contract() -> None:
    state = _state()
    orchestrator, mapper = _orchestrator(
        LlmMappingResult(
            raw_response="{}",
            parsed_json={},
            draft=LlmVisualPlanDraft(
                visual_kind="chart",
                intent="compare_categories",
                action="create_plan",
                chart_type="donut",
                roles={
                    "category": {"field": "Region"},
                    "measure": {"field": "Amount", "aggregation": "sum"},
                },
                renderer="plotly",
            ),
        )
    )

    result = orchestrator.handle_message("make a donut chart", state, use_llm=True)
    assert mapper.calls == 1
    assert result.action == "unsupported"
    assert result.visual_plan is None
    assert result.trace is not None
    assert result.trace.validation_success is False
    assert any(
        "Unsupported chart_type: donut." in message
        for message in result.trace.validation_errors
    )
