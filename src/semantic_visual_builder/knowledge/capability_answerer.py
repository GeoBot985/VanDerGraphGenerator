"""Answer capability questions from the product knowledge base."""

from __future__ import annotations

from semantic_visual_builder.knowledge.product_kb import ProductKnowledgeBase


class CapabilityAnswerer:
    """Produce KB-grounded responses for feature questions."""

    def __init__(self, product_kb: ProductKnowledgeBase):
        self.product_kb = product_kb

    def answer(self, question: str) -> str:
        text = question.lower()
        chart_names = [item.get("name", "") for item in self.product_kb.chart_types.get("supported_mvp", []) if isinstance(item, dict)]
        diagram_names = [item.get("name", "") for item in self.product_kb.diagram_types.get("supported_mvp", []) if isinstance(item, dict)]

        if "generated python" in text or "python renderer" in text:
            return (
                "Generated Python rendering is planned as a future renderer plugin. It is not active in the MVP. "
                "The MVP uses Mermaid for diagrams and Plotly/Chart.js-style deterministic chart specifications for data graphs."
            )
        if "graphviz" in text:
            return "Graphviz is not part of the MVP. The MVP uses Mermaid for supported diagram plans."
        if "flowchart" in text or "flowcharts" in text:
            return (
                "Flowcharts are supported as an MVP diagram target through Mermaid. The app can build a validated diagram plan, "
                "with rendering added in a later sprint."
            )
        if "what chart types" in text or "supported charts" in text:
            return f"Supported MVP chart types are: {', '.join([name for name in chart_names if name])}."
        if "what diagram types" in text or "supported diagrams" in text:
            return f"Supported MVP diagram types are: {', '.join([name for name in diagram_names if name])}."
        if "what can" in text or "capabilities" in text or "what does this app do" in text:
            mvp_caps = self.product_kb.capabilities.get("mvp_capabilities", [])
            future_caps = self.product_kb.capabilities.get("future_capabilities", [])
            return (
                "MVP capabilities include: "
                f"{', '.join(mvp_caps)}. "
                f"Planned future capabilities include: {', '.join(future_caps)}."
            )
        if "powerpoint" in text or "word report" in text:
            return "PowerPoint and Word output are future capabilities, not MVP-supported."
        return "The KB does not list that feature yet."
