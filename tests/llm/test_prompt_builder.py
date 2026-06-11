"""Prompt builder tests."""

from pathlib import Path

from semantic_visual_builder.data.csv_loader import CsvLoader
from semantic_visual_builder.data.data_profiler import DataProfiler
from semantic_visual_builder.knowledge.graph_matrix import GraphMatrixLoader
from semantic_visual_builder.knowledge.product_kb import ProductKnowledgeLoader
from semantic_visual_builder.llm.prompt_builder import VisualIntentPromptBuilder
from semantic_visual_builder.utils.paths import get_graph_matrix_dir, get_kb_dir


def test_prompt_includes_user_request_columns_and_contract() -> None:
    root = Path(__file__).resolve().parents[2]
    loaded = CsvLoader().load(root / "assets" / "samples" / "sample_transactions.csv")
    profile = DataProfiler().profile(loaded.dataframe)
    kb = ProductKnowledgeLoader(get_kb_dir()).load()
    graph_matrix = GraphMatrixLoader(
        get_graph_matrix_dir() / "graph_matrix.json"
    ).load()
    prompt = VisualIntentPromptBuilder().build_prompt(
        user_message="Show transactions per week",
        dataset_profile=profile,
        product_kb=kb,
        graph_matrix=graph_matrix,
    )

    assert "Show transactions per week" in prompt
    assert "TransactionDate" in prompt
    assert "graph matrix authoritative contract" in prompt.lower()
    assert '"action"' in prompt
    assert "create_plan" in prompt
    assert '"title_size":null' in prompt
    assert '"palette":{"primary":null,"secondary":null,"accent":null,"sequence":[]}' in prompt
    assert "style.palette.primary or style.palette.sequence" in prompt
    assert "style.title_size as an integer" in prompt
    assert "schema_version" in prompt
    assert "required json output contract" in prompt.lower()
    assert "TransactionDate,Region,Status,Amount" not in prompt
