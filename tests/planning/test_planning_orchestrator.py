"""Planning orchestrator tests."""

from pathlib import Path

from semantic_visual_builder.data.csv_loader import CsvLoader
from semantic_visual_builder.data.data_profiler import DataProfiler
from semantic_visual_builder.knowledge.graph_matrix import GraphMatrixLoader
from semantic_visual_builder.knowledge.product_kb import ProductKnowledgeLoader
from semantic_visual_builder.llm.llm_mapping_result import LlmMappingResult, LlmVisualPlanDraft
from semantic_visual_builder.planning.field_mapper import FieldMapper
from semantic_visual_builder.planning.intent_mapper import IntentMapper
from semantic_visual_builder.planning.planning_orchestrator import PlanningOrchestrator
from semantic_visual_builder.state.app_state import AppState
from semantic_visual_builder.utils.paths import get_graph_matrix_dir, get_kb_dir
from semantic_visual_builder.validation.capability_validator import CapabilityValidator
from semantic_visual_builder.validation.visual_plan_validator import VisualPlanValidator


class FakeLlmMapper:
    def __init__(self, result):
        self.result = result
        self.calls = 0

    def map_to_draft(self, **kwargs):
        self.calls += 1
        return self.result


def _app_state(selected_model="gemma4:12b"):
    root = Path(__file__).resolve().parents[2]
    loaded = CsvLoader().load(root / "assets" / "samples" / "sample_transactions.csv")
    profile = DataProfiler().profile(loaded.dataframe)
    state = AppState()
    state.dataset_context.loaded_dataset = loaded
    state.dataset_context.profile = profile
    state.product_kb = ProductKnowledgeLoader(get_kb_dir()).load()
    state.graph_matrix = GraphMatrixLoader(get_graph_matrix_dir() / "graph_matrix.json").load()
    state.model_registry.selected_model = selected_model
    return state


def _orchestrator(fake_result):
    return PlanningOrchestrator(
        llm_mapper=FakeLlmMapper(fake_result),
        deterministic_mapper=IntentMapper(),
        field_mapper=FieldMapper(),
        visual_plan_validator=VisualPlanValidator(),
        capability_validator=CapabilityValidator(),
    )


def test_uses_llm_when_enabled_and_model_selected() -> None:
    draft = LlmVisualPlanDraft(
        visual_kind="chart",
        intent="compare_categories",
        chart_type="bar",
        roles={
            "category": {"field": "Region"},
            "measure": {"field": "Amount", "aggregation": "sum"},
        },
        renderer="plotly",
    )
    result = _orchestrator(LlmMappingResult(raw_response="{}", parsed_json={}, draft=draft)).create_or_update_plan("Show total amount by region", _app_state(), use_llm=True)
    assert result.mapping_method == "llm"
    assert result.used_fallback is False
    assert result.llm_mapping_result is not None


def test_uses_deterministic_fallback_when_llm_disabled() -> None:
    state = _app_state()
    state.set_llm_mapping_enabled(False)
    result = _orchestrator(None).create_or_update_plan("Show transactions per week", state, use_llm=True)
    assert result.mapping_method == "deterministic"
    assert result.used_fallback is False


def test_uses_deterministic_fallback_when_ollama_fails() -> None:
    result = _orchestrator(LlmMappingResult(raw_response="", parsed_json=None, draft=None, errors=["offline"])).create_or_update_plan("Show transactions per week", _app_state(), use_llm=True)
    assert result.mapping_method == "deterministic_fallback"
    assert result.used_fallback is True


def test_rejects_unsupported_llm_renderer_and_falls_back() -> None:
    draft = LlmVisualPlanDraft(
        visual_kind="chart",
        intent="compare_categories",
        chart_type="bar",
        roles={
            "category": {"field": "Region"},
            "measure": {"field": "Amount", "aggregation": "sum"},
        },
        renderer="python",
    )
    result = _orchestrator(LlmMappingResult(raw_response="{}", parsed_json={}, draft=draft)).create_or_update_plan("Show total amount by region", _app_state(), use_llm=True)
    assert result.mapping_method == "deterministic_fallback"
    assert result.used_fallback is True


def test_stores_mapping_method_correctly() -> None:
    draft = LlmVisualPlanDraft(
        visual_kind="chart",
        intent="compare_categories",
        chart_type="bar",
        roles={
            "category": {"field": "Region"},
            "measure": {"field": "Amount", "aggregation": "sum"},
        },
        renderer="plotly",
    )
    result = _orchestrator(LlmMappingResult(raw_response="{}", parsed_json={}, draft=draft, used_repair=True)).create_or_update_plan("Show total amount by region", _app_state(), use_llm=True)
    assert result.mapping_method == "llm_with_repair"
