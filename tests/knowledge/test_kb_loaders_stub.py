"""Knowledge loader tests."""

from semantic_visual_builder.knowledge.graph_matrix import GraphMatrixLoader
from semantic_visual_builder.knowledge.product_kb import ProductKnowledgeLoader
from semantic_visual_builder.utils.paths import get_graph_matrix_dir, get_kb_dir


def test_product_kb_loads_capabilities() -> None:
    kb = ProductKnowledgeLoader(get_kb_dir()).load()
    assert kb.capabilities["internal_name"] == "semantic_visual_builder"


def test_graph_matrix_loads_intents() -> None:
    matrix = GraphMatrixLoader(get_graph_matrix_dir() / "graph_matrix.json").load()
    assert matrix.list_intents() == [
        "compare_categories",
        "show_trend",
        "show_process",
        "show_distribution",
        "show_matrix",
        "compare_stacked_categories",
        "show_relationship",
        "show_single_value",
    ]
    assert matrix.schema_version() == "1.1"
    assert matrix.supported_chart_types() == [
        "bar",
        "horizontal_bar",
        "line",
        "area",
        "stacked_area",
        "scatter",
        "bubble",
        "pie",
        "donut",
        "histogram",
        "box_plot",
        "heatmap",
        "stacked_bar",
        "treemap",
        "waterfall",
        "funnel",
        "radar",
        "gauge",
        "kpi_card",
    ]
    assert matrix.supported_diagram_types() == [
        "flowchart",
        "sequence_diagram",
        "erd",
        "network_diagram",
        "timeline",
        "swimlane",
    ]
    assert matrix.required_roles_for("stacked_bar") == ["category", "stack", "measure"]
    assert matrix.get_visual_spec("histogram")["required_roles"] == ["value"]
    assert matrix.get_visual_spec("sequence_diagram")["allowed_renderers"] == [
        "mermaid"
    ]
    assert matrix.renderer_allowed("flowchart", "mermaid") is True
    assert matrix.renderer_allowed("donut", "plotly") is True
