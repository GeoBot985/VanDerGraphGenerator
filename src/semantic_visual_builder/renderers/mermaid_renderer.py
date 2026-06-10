"""Mermaid renderer implementation."""

from __future__ import annotations

from semantic_visual_builder.utils.text_sanitize import sanitize_label
from semantic_visual_builder.data.dataset_context import DatasetContext
from semantic_visual_builder.planning.visual_plan_schema import DiagramEdge, DiagramNode, VisualPlan
from semantic_visual_builder.renderers.base_renderer import BaseRenderer
from semantic_visual_builder.renderers.renderer_result import RendererOutput
from semantic_visual_builder.validation.validation_result import ValidationResult


class MermaidRenderer(BaseRenderer):
    """Render basic flowchart plans to Mermaid syntax."""

    name = "mermaid"

    def can_render(self, visual_plan: VisualPlan) -> bool:
        return visual_plan.visual_kind == "diagram" and visual_plan.diagram_type == "flowchart"

    def render(
        self,
        visual_plan: VisualPlan,
        dataset_context: DatasetContext | None = None,
    ) -> RendererOutput:
        if not self.can_render(visual_plan):
            raise ValueError("MermaidRenderer can only render flowchart diagram plans.")
        code = self._build_mermaid(visual_plan)
        return RendererOutput(renderer_name=self.name, output_type="mermaid", content=code)

    def validate_output(self, output: RendererOutput) -> ValidationResult:
        result = ValidationResult()
        if output.output_type != "mermaid":
            result.add_error("output_type must be mermaid.")
        if not output.content.strip():
            result.add_error("Mermaid output must not be blank.")
        if not output.content.lstrip().startswith("flowchart"):
            result.add_error("Mermaid flowchart output must start with flowchart.")
        if "-->" not in output.content:
            result.add_error("Mermaid output must contain at least one edge arrow.")
        return result

    def _build_mermaid(self, visual_plan: VisualPlan) -> str:
        nodes = visual_plan.diagram_nodes or self._fallback_nodes()
        edges = visual_plan.diagram_edges or self._fallback_edges(nodes)
        direction = "LR" if visual_plan.style.orientation == "horizontal" else "TD"
        lines = [f"flowchart {direction}"]
        for node in nodes:
            lines.append(f"    {self._safe_node_id(node.id)}{self._node_brackets(node)}")
        for edge in edges:
            if edge.label:
                lines.append(f"    {self._safe_node_id(edge.source)} -->|{sanitize_label(edge.label)}| {self._safe_node_id(edge.target)}")
            else:
                lines.append(f"    {self._safe_node_id(edge.source)} --> {self._safe_node_id(edge.target)}")
        return "\n".join(lines)

    def _node_brackets(self, node: DiagramNode) -> str:
        label = sanitize_label(node.label)
        if node.node_type == "decision":
            return f"{{{label}}}"
        if node.node_type in {"start", "end"}:
            return f"([{label}])"
        return f"[{label}]"

    def _safe_node_id(self, node_id: str) -> str:
        return "".join(ch for ch in node_id if ch.isalnum() or ch == "_")

    def _fallback_nodes(self) -> list[DiagramNode]:
        return [
            DiagramNode(id="A", label="Diagram plan created"),
            DiagramNode(id="B", label="Detailed node extraction starts in a later sprint"),
        ]

    def _fallback_edges(self, nodes: list[DiagramNode]) -> list[DiagramEdge]:
        if len(nodes) < 2:
            return []
        return [DiagramEdge(source=nodes[0].id, target=nodes[1].id)]
