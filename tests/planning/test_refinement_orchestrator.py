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


def test_deterministic_refinement_updates_explicit_chart_type_change() -> None:
    current_plan = VisualPlan(
        visual_kind="chart",
        intent="compare_categories",
        chart_type="pie",
        data_roles=[
            DataRole(role="category", field="Region"),
            DataRole(role="measure", field="Amount", aggregation="count"),
        ],
    )
    current_plan.render_target.renderer = "plotly"
    state = _state()
    state.model_registry.selected_model = None

    result = _orchestrator(
        LlmMappingResult(raw_response="", parsed_json=None, draft=None, errors=["off"])
    ).refine_plan(current_plan, "change it to a bar chart", state, use_llm=True)

    assert result.used_fallback is True
    assert result.visual_plan is not None
    assert result.visual_plan.chart_type == "bar"


def test_deterministic_refinement_realigns_roles_when_switching_to_line() -> None:
    current_plan = VisualPlan(
        visual_kind="chart",
        intent="compare_categories",
        chart_type="pie",
        data_roles=[
            DataRole(role="category", field="Region"),
            DataRole(role="measure", field="Amount", aggregation="sum"),
        ],
    )
    current_plan.render_target.renderer = "plotly"
    state = _state()
    state.model_registry.selected_model = None

    result = _orchestrator(
        LlmMappingResult(raw_response="", parsed_json=None, draft=None, errors=["off"])
    ).refine_plan(current_plan, "please change to a line graph", state, use_llm=True)

    assert result.used_fallback is True
    assert result.visual_plan is not None
    assert result.visual_plan.chart_type == "line"
    assert {role.role for role in result.visual_plan.data_roles} == {"x", "y"}


def test_deterministic_refinement_sets_background_colour() -> None:
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
    state = _state()
    state.model_registry.selected_model = None

    result = _orchestrator(
        LlmMappingResult(raw_response="", parsed_json=None, draft=None, errors=["off"])
    ).refine_plan(
        current_plan, "please make the background light green", state, use_llm=True
    )

    assert result.used_fallback is True
    assert result.visual_plan is not None
    assert result.visual_plan.style.background == "#90ee90"
    assert result.visual_plan.style.plot_background == "#90ee90"


def test_deterministic_refinement_sets_series_colour() -> None:
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
    state = _state()
    state.model_registry.selected_model = None

    result = _orchestrator(
        LlmMappingResult(raw_response="", parsed_json=None, draft=None, errors=["off"])
    ).refine_plan(
        current_plan,
        "please make the bars light grey",
        state,
        use_llm=True,
    )

    assert result.used_fallback is True
    assert result.visual_plan is not None
    assert result.visual_plan.style.palette["primary"] == "#d3d3d3"


def test_llm_noop_style_refinement_uses_deterministic_style_patch() -> None:
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
                chart_type="bar",
                roles={
                    "category": {"field": "Region"},
                    "measure": {"field": "Amount", "aggregation": "sum"},
                },
                style={},
                renderer="plotly",
            ),
        )
    ).refine_plan(current_plan, "please make the background light green", _state())

    assert result.used_fallback is False
    assert result.visual_plan is not None
    assert result.visual_plan.style.background == "#90ee90"
    assert any("deterministic style refinement" in message for message in result.messages)


def test_llm_partial_style_refinement_keeps_llm_background_and_adds_missing_series_colour() -> None:
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
                chart_type="bar",
                roles={
                    "category": {"field": "Region"},
                    "measure": {"field": "Amount", "aggregation": "sum"},
                },
                style={"background": "#333333", "plot_background": "#333333"},
                renderer="plotly",
            ),
        )
    ).refine_plan(
        current_plan,
        "make the background dark grey and the bars light grey",
        _state(),
    )

    assert result.used_fallback is False
    assert result.visual_plan is not None
    assert result.visual_plan.style.background == "#333333"
    assert result.visual_plan.style.plot_background == "#333333"
    assert result.visual_plan.style.palette["primary"] == "#d3d3d3"
    assert any("deterministic style refinement" in message for message in result.messages)


def test_llm_partial_style_refinement_keeps_llm_title_and_adds_missing_title_size() -> None:
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
                chart_type="bar",
                roles={
                    "category": {"field": "Region"},
                    "measure": {"field": "Amount", "aggregation": "sum"},
                },
                style={"title": "Bollocks Chart"},
                renderer="plotly",
            ),
        )
    ).refine_plan(
        current_plan,
        'make the Title "Bollocks Chart" and make it 2x bigger',
        _state(),
    )

    assert result.used_fallback is False
    assert result.visual_plan is not None
    assert result.visual_plan.style.title == "Bollocks Chart"
    assert result.visual_plan.style.title_size == 32
    assert any("deterministic style refinement" in message for message in result.messages)


def test_llm_structured_background_refinement_is_normalised() -> None:
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
            ),
        )
    ).refine_plan(current_plan, "set background colour to light green", _state())

    assert result.used_fallback is False
    assert result.visual_plan is not None
    assert result.visual_plan.style.background == "#e6ffe6"
    assert result.visual_plan.style.plot_background == "#e6ffe6"


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
