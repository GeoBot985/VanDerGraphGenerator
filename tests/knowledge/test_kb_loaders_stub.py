"""Knowledge loader tests."""

from pathlib import Path

from semantic_visual_builder.knowledge.graph_matrix import GraphMatrixLoader
from semantic_visual_builder.knowledge.product_kb import ProductKnowledgeLoader
from semantic_visual_builder.utils.paths import get_graph_matrix_dir, get_kb_dir


def test_product_kb_loads_capabilities() -> None:
    kb = ProductKnowledgeLoader(get_kb_dir()).load()
    assert kb.capabilities["internal_name"] == "semantic_visual_builder"


def test_graph_matrix_loads_intents() -> None:
    matrix = GraphMatrixLoader(get_graph_matrix_dir() / "graph_matrix.json").load()
    assert matrix.list_intents() == ["compare_categories", "show_trend", "show_process"]
