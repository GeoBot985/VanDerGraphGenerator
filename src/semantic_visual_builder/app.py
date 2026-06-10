"""Application bootstrap."""

from __future__ import annotations

from semantic_visual_builder.data.dataset_context import DatasetContext
from semantic_visual_builder.knowledge.graph_matrix import GraphMatrixLoader
from semantic_visual_builder.knowledge.product_kb import ProductKnowledgeLoader
from semantic_visual_builder.state.app_state import AppState
from semantic_visual_builder.ui.tkinter_app import SemanticVisualBuilderApp
from semantic_visual_builder.utils.logging_config import configure_logging
from semantic_visual_builder.utils.paths import get_graph_matrix_dir, get_kb_dir


def create_app_state() -> AppState:
    state = AppState()
    try:
        state.product_kb = ProductKnowledgeLoader(get_kb_dir()).load()
    except Exception as exc:
        state.add_status(f"Product KB load failed: {exc}")
    try:
        state.graph_matrix = GraphMatrixLoader(get_graph_matrix_dir() / "graph_matrix.json").load()
    except Exception as exc:
        state.add_status(f"Graph matrix load failed: {exc}")
    return state


def main() -> None:
    configure_logging()
    app = SemanticVisualBuilderApp(create_app_state())
    app.run()
