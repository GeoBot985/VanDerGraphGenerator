"""Product knowledge base loading helpers."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from semantic_visual_builder.utils.json_utils import load_json


@dataclass
class ProductKnowledgeBase:
    """Structured product knowledge loaded from local files."""

    capabilities: dict[str, Any]
    limitations: dict[str, Any]
    workflow: dict[str, Any]
    chart_types: dict[str, Any] = field(default_factory=dict)
    diagram_types: dict[str, Any] = field(default_factory=dict)


class ProductKnowledgeLoader:
    """Load local product knowledge files."""

    def __init__(self, kb_dir: Path):
        self.kb_dir = kb_dir

    def load(self) -> ProductKnowledgeBase:
        capabilities = load_json(self.kb_dir / "capabilities.json")
        limitations = load_json(self.kb_dir / "limitations.json")
        workflow = load_json(self.kb_dir / "workflow.json")
        chart_types = load_json(self.kb_dir / "chart_types.json")
        diagram_types = load_json(self.kb_dir / "diagram_types.json")
        return ProductKnowledgeBase(
            capabilities=capabilities,
            limitations=limitations,
            workflow=workflow,
            chart_types=chart_types,
            diagram_types=diagram_types,
        )


def summarize_capabilities(kb: ProductKnowledgeBase) -> str:
    """Return a short human-readable summary."""

    capabilities = kb.capabilities.get("mvp_capabilities", [])
    limitations = kb.limitations.get("mvp_limitations", [])
    chart_types = [item.get("name", "") for item in kb.chart_types.get("supported_mvp", []) if isinstance(item, dict)]
    diagram_types = [item.get("name", "") for item in kb.diagram_types.get("supported_mvp", []) if isinstance(item, dict)]
    return (
        f"MVP capabilities: {', '.join(capabilities)}\n"
        f"Supported chart types: {', '.join([name for name in chart_types if name])}\n"
        f"Supported diagram types: {', '.join([name for name in diagram_types if name])}\n"
        f"Limitations: {', '.join(limitations)}"
    )
