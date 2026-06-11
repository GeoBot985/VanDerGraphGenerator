"""LLM semantic mapper tests."""

from semantic_visual_builder.data.csv_loader import CsvLoader
from semantic_visual_builder.data.data_profiler import DataProfiler
from semantic_visual_builder.knowledge.graph_matrix import GraphMatrixLoader
from semantic_visual_builder.knowledge.product_kb import ProductKnowledgeLoader
from semantic_visual_builder.llm.json_repair import JsonRepair
from semantic_visual_builder.llm.llm_response_parser import LlmResponseParser
from semantic_visual_builder.llm.llm_semantic_mapper import LlmSemanticMapper
from semantic_visual_builder.llm.prompt_builder import VisualIntentPromptBuilder
from semantic_visual_builder.utils.paths import get_graph_matrix_dir, get_kb_dir
from semantic_visual_builder.validation.llm_output_validator import LlmOutputValidator


class FakeClient:
    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = []

    def generate(self, model, prompt, system=None, temperature=0.0):
        self.calls.append(
            {
                "model": model,
                "prompt": prompt,
                "system": system,
                "temperature": temperature,
            }
        )
        response = self.responses.pop(0)
        if isinstance(response, Exception):
            raise response
        return response


def _profile():
    root = __import__("pathlib").Path(__file__).resolve().parents[2]
    loaded = CsvLoader().load(root / "assets" / "samples" / "sample_transactions.csv")
    return DataProfiler().profile(loaded.dataframe)


def _mapper(client):
    return LlmSemanticMapper(
        ollama_client=client,
        prompt_builder=VisualIntentPromptBuilder(),
        response_parser=LlmResponseParser(),
        output_validator=LlmOutputValidator(),
        json_repair=JsonRepair(),
    )


def test_valid_llm_json_returns_draft() -> None:
    client = FakeClient(
        [
            '{"action":"create_plan","visual_kind":"chart","intent":"compare_categories","chart_type":"bar","roles":{"category":{"field":"Region"},"measure":{"field":"Amount","aggregation":"sum"}},"renderer":"plotly"}'
        ]
    )
    result = _mapper(client).map_to_draft(
        "model",
        "Show total amount by region",
        _profile(),
        ProductKnowledgeLoader(get_kb_dir()).load(),
        GraphMatrixLoader(get_graph_matrix_dir() / "graph_matrix.json").load(),
    )
    assert result.draft is not None
    assert result.used_repair is False


def test_fenced_json_is_accepted() -> None:
    client = FakeClient(
        [
            '```json\n{"action":"create_plan","visual_kind":"diagram","intent":"show_process","diagram_type":"flowchart","roles":{"nodes":{},"edges":{}},"diagram_nodes":[{"id":"A","label":"User"},{"id":"B","label":"App"}],"diagram_edges":[{"source":"A","target":"B"}],"renderer":"mermaid"}\n```'
        ]
    )
    result = _mapper(client).map_to_draft(
        "model",
        "Create a flowchart",
        _profile(),
        ProductKnowledgeLoader(get_kb_dir()).load(),
        GraphMatrixLoader(get_graph_matrix_dir() / "graph_matrix.json").load(),
    )
    assert result.draft is not None


def test_malformed_json_triggers_repair() -> None:
    client = FakeClient(
        [
            "not json",
            '{"action":"create_plan","visual_kind":"chart","intent":"compare_categories","chart_type":"bar","roles":{"category":{"field":"Region"},"measure":{"field":"Amount","aggregation":"sum"}},"renderer":"plotly"}',
        ]
    )
    result = _mapper(client).map_to_draft(
        "model",
        "Show total amount by region",
        _profile(),
        ProductKnowledgeLoader(get_kb_dir()).load(),
        GraphMatrixLoader(get_graph_matrix_dir() / "graph_matrix.json").load(),
    )
    assert result.used_repair is True
    assert result.draft is not None


def test_invalid_output_returns_errors() -> None:
    client = FakeClient(
        [
            '{"action":"create_plan","visual_kind":"chart","intent":"compare_categories","chart_type":"donut","roles":{"category":{"field":"Region"},"measure":{"field":"Amount","aggregation":"sum"}},"renderer":"plotly"}'
        ]
    )
    result = _mapper(client).map_to_draft(
        "model",
        "Show total amount by region",
        _profile(),
        ProductKnowledgeLoader(get_kb_dir()).load(),
        GraphMatrixLoader(get_graph_matrix_dir() / "graph_matrix.json").load(),
    )
    assert result.draft is None
    assert result.errors


def test_generation_failure_returns_mapping_result_with_errors() -> None:
    client = FakeClient([RuntimeError("offline")])
    result = _mapper(client).map_to_draft(
        "model",
        "Show total amount by region",
        _profile(),
        ProductKnowledgeLoader(get_kb_dir()).load(),
        GraphMatrixLoader(get_graph_matrix_dir() / "graph_matrix.json").load(),
    )
    assert result.draft is None
    assert result.errors
