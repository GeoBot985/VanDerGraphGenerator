"""Product knowledge base loading helpers."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from semantic_visual_builder.utils.json_utils import load_json


@dataclass
class ProductKnowledgeBase:
    """Structured product knowledge loaded from local files."""

    capabilities: dict[str, Any]
    limitations: dict[str, Any]
    workflow: dict[str, Any]


class ProductKnowledgeLoader:
    """Load local product knowledge files."""

    def __init__(self, kb_dir: Path):
        self.kb_dir = kb_dir

    def load(self) -> ProductKnowledgeBase:
        capabilities = load_json(self.kb_dir / "capabilities.json")
        limitations = load_json(self.kb_dir / "limitations.json")
        workflow = load_json(self.kb_dir / "workflow.json")
        return ProductKnowledgeBase(capabilities=capabilities, limitations=limitations, workflow=workflow)


def summarize_capabilities(kb: ProductKnowledgeBase) -> str:
    """Return a short human-readable summary."""

    capabilities = kb.capabilities.get("mvp_capabilities", [])
    limitations = kb.limitations.get("mvp_limitations", [])
    return (
        f"MVP capabilities: {', '.join(capabilities)}\n"
        f"Limitations: {', '.join(limitations)}"
    )
