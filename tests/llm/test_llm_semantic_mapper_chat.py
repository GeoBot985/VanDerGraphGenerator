"""Tests for LlmSemanticMapper.map_to_draft_with_history (chat-based refinement)."""

from __future__ import annotations

from pathlib import Path

from semantic_visual_builder.data.csv_loader import CsvLoader
from semantic_visual_builder.data.data_profiler import DataProfiler
from semantic_visual_builder.knowledge.graph_matrix import GraphMatrixLoader
from semantic_visual_builder.knowledge.product_kb import ProductKnowledgeLoader
from semantic_visual_builder.llm.json_repair import JsonRepair
from semantic_visual_builder.llm.llm_response_parser import LlmResponseParser
from semantic_visual_builder.llm.llm_semantic_mapper import LlmSemanticMapper
from semantic_visual_builder.llm.prompt_builder import VisualIntentPromptBuilder
from semantic_visual_builder.planning.visual_plan_schema import DataRole, VisualPlan
from semantic_visual_builder.utils.paths import get_graph_matrix_dir, get_kb_dir
from semantic_visual_builder.validation.llm_output_validator import LlmOutputValidator


class ChatFakeClient:
    def __init__(self, chat_response: str) -> None:
        self.chat_response = chat_response
        self.chat_calls: list[dict] = []

    def chat(self, model, messages, system=None, temperature=0.0, num_predict=256, response_format="json"):
        self.chat_calls.append(
            {
                "model": model,
                "messages": list(messages),
                "system": system,
                "temperature": temperature,
                "response_format": response_format,
            }
        )
        return self.chat_response


def _profile():
    root = Path(__file__).resolve().parents[2]
    loaded = CsvLoader().load(root / "assets" / "samples" / "sample_transactions.csv")
    return DataProfiler().profile(loaded.dataframe)


def _graph_matrix():
    return GraphMatrixLoader(get_graph_matrix_dir() / "graph_matrix.json").load()


def _product_kb():
    return ProductKnowledgeLoader(get_kb_dir()).load()


def _mapper(client):
    return LlmSemanticMapper(
        ollama_client=client,
        prompt_builder=VisualIntentPromptBuilder(),
        response_parser=LlmResponseParser(),
        output_validator=LlmOutputValidator(),
        json_repair=JsonRepair(),
    )


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


def test_chat_history_path_sends_history_then_structured_prompt() -> None:
    payload = (
        '{"action":"create_plan","visual_kind":"chart",'
        '"intent":"compare_categories","chart_type":"bar",'
        '"roles":{"category":{"field":"Region"},"measure":{"field":"Amount","aggregation":"sum"}},'
        '"renderer":"plotly"}'
    )
    client = ChatFakeClient(payload)
    history = [
        {"role": "user", "content": "Show total amount by region"},
        {"role": "assistant", "content": "Here is a bar chart."},
    ]
    result = _mapper(client).map_to_draft_with_history(
        model="gemma4:12b",
        user_message="Keep it as a bar chart but refine",
        dataset_profile=_profile(),
        product_kb=_product_kb(),
        graph_matrix=_graph_matrix(),
        current_plan=_plan(),
        conversation_messages=history,
    )
    assert result.draft is not None
    assert result.draft.chart_type == "bar"
    assert len(client.chat_calls) == 1
    call = client.chat_calls[0]
    assert call["model"] == "gemma4:12b"
    # Two history turns + the final structured prompt as a user message.
    assert len(call["messages"]) == 3
    assert call["messages"][0] == {"role": "user", "content": "Show total amount by region"}
    assert call["messages"][1] == {"role": "assistant", "content": "Here is a bar chart."}
    assert call["messages"][2]["role"] == "user"
    assert "Keep it as a bar chart but refine" in call["messages"][2]["content"]


def test_chat_history_path_skips_empty_turns() -> None:
    payload = (
        '{"action":"create_plan","visual_kind":"chart",'
        '"intent":"compare_categories","chart_type":"bar",'
        '"roles":{"category":{"field":"Region"},"measure":{"field":"Amount","aggregation":"sum"}},'
        '"renderer":"plotly"}'
    )
    client = ChatFakeClient(payload)
    history = [
        {"role": "user", "content": "  "},
        {"role": "assistant", "content": "valid"},
        {"role": "system", "content": "ignored"},
    ]
    _mapper(client).map_to_draft_with_history(
        model="m",
        user_message="Keep it as a bar chart but refine",
        dataset_profile=_profile(),
        product_kb=_product_kb(),
        graph_matrix=_graph_matrix(),
        current_plan=_plan(),
        conversation_messages=history,
    )
    call = client.chat_calls[0]
    # Only the non-empty assistant turn survives, plus the final prompt.
    assert [m["role"] for m in call["messages"]] == ["assistant", "user"]


def test_chat_history_path_returns_error_when_chat_raises() -> None:
    class RaisingClient(ChatFakeClient):
        def chat(self, *args, **kwargs):
            raise RuntimeError("ollama down")

    client = RaisingClient("")
    result = _mapper(client).map_to_draft_with_history(
        model="m",
        user_message="Keep it as a bar chart but refine",
        dataset_profile=_profile(),
        product_kb=_product_kb(),
        graph_matrix=_graph_matrix(),
        current_plan=_plan(),
        conversation_messages=[{"role": "user", "content": "hi"}],
    )
    assert result.draft is None
    assert result.errors and "ollama down" in result.errors[0]
