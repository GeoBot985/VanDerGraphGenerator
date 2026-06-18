"""Mermaid renderer implementation."""

from __future__ import annotations

from semantic_visual_builder.data.dataset_context import DatasetContext
from semantic_visual_builder.planning.visual_plan_schema import (
    DiagramEdge,
    DiagramNode,
    VisualPlan,
)
from semantic_visual_builder.renderers.base_renderer import BaseRenderer
from semantic_visual_builder.renderers.mermaid_style_adapter import (
    MermaidStyleAdapter,
    _3d_node_shape,
    mermaid_chart_style,
)
from semantic_visual_builder.renderers.renderer_result import RendererOutput
from semantic_visual_builder.utils.text_sanitize import sanitize_label
from semantic_visual_builder.validation.validation_result import ValidationResult


class MermaidRenderer(BaseRenderer):
    """Render basic flowchart plans to Mermaid syntax."""

    name = "mermaid"

    def __init__(self) -> None:
        self.style_adapter = MermaidStyleAdapter()

    def can_render(self, visual_plan: VisualPlan) -> bool:
        return visual_plan.visual_kind == "diagram" and visual_plan.diagram_type in {
            "flowchart",
            "sequence_diagram",
            "erd",
            "network_diagram",
            "timeline",
            "swimlane",
        }

    def render(
        self,
        visual_plan: VisualPlan,
        dataset_context: DatasetContext | None = None,
    ) -> RendererOutput:
        if not self.can_render(visual_plan):
            raise ValueError(
                "MermaidRenderer can only render supported Mermaid diagram plans."
            )
        code = self._build_mermaid(visual_plan)
        code = self.style_adapter.apply_style_to_mermaid(code, visual_plan)
        return RendererOutput(
            renderer_name=self.name,
            output_type="mermaid",
            content=code,
            metadata={
                "style_profile_id": visual_plan.metadata.style_profile_id,
                "style_profile_name": visual_plan.metadata.style_profile_name,
            },
        )

    def validate_output(self, output: RendererOutput) -> ValidationResult:
        result = ValidationResult()
        if output.output_type != "mermaid":
            result.add_error("output_type must be mermaid.")
        if not output.content.strip():
            result.add_error("Mermaid output must not be blank.")
        if not (
            output.content.lstrip().startswith("flowchart")
            or output.content.lstrip().startswith("sequenceDiagram")
            or output.content.lstrip().startswith("erDiagram")
            or output.content.lstrip().startswith("timeline")
        ):
            result.add_error(
                "Mermaid output must start with a supported Mermaid diagram header."
            )
        if (
            "-->" not in output.content
            and "->>" not in output.content
            and "||--" not in output.content
            and " : " not in output.content
        ):
            result.add_error("Mermaid output must contain at least one edge arrow.")
        return result

    def _build_mermaid(self, visual_plan: VisualPlan) -> str:
        if visual_plan.diagram_type == "sequence_diagram":
            return self._build_sequence_diagram(visual_plan)
        if visual_plan.diagram_type == "erd":
            return self._build_erd(visual_plan)
        if visual_plan.diagram_type == "timeline":
            return self._build_timeline(visual_plan)
        if visual_plan.diagram_type == "swimlane":
            return self._build_swimlane(visual_plan)
        if visual_plan.diagram_type == "network_diagram":
            return self._build_network_diagram(visual_plan)
        nodes = visual_plan.diagram_nodes or self._fallback_nodes()
        edges = visual_plan.diagram_edges or self._fallback_edges(nodes)
        direction = visual_plan.style.diagram_direction or (
            "LR" if visual_plan.style.orientation == "horizontal" else "TD"
        )
        lines = [f"flowchart {direction}"]
        for node in nodes:
            lines.append(
                f"    {self._safe_node_id(node.id)}{self._node_brackets(node, visual_plan)}"
            )
        for edge in edges:
            if edge.label:
                source = self._safe_node_id(edge.source)
                target = self._safe_node_id(edge.target)
                label = sanitize_label(edge.label)
                lines.append(
                    f"    {source} -->|{label}| {target}"
                )
            else:
                source = self._safe_node_id(edge.source)
                target = self._safe_node_id(edge.target)
                lines.append(
                    f"    {source} --> {target}"
                )
        return "\n".join(lines)

    def _build_sequence_diagram(self, visual_plan: VisualPlan) -> str:
        nodes = visual_plan.diagram_nodes or self._fallback_nodes()
        edges = visual_plan.diagram_edges or self._fallback_edges(nodes)
        lines = ["sequenceDiagram"]
        for node in nodes:
            node_id = self._safe_node_id(node.id)
            node_label = sanitize_label(node.label)
            lines.append(f"    participant {node_id} as {node_label}")
        for edge in edges:
            label = sanitize_label(edge.label) if edge.label else "message"
            source = self._safe_node_id(edge.source)
            target = self._safe_node_id(edge.target)
            lines.append(f"    {source}->>{target}: {label}")
        return "\n".join(lines)

    def _build_erd(self, visual_plan: VisualPlan) -> str:
        nodes = visual_plan.diagram_nodes or self._fallback_nodes()
        edges = visual_plan.diagram_edges or self._fallback_edges(nodes)
        lines = ["erDiagram"]
        for node in nodes:
            node_id = self._safe_node_id(node.id)
            node_label = sanitize_label(node.label)
            lines.append(f"    {node_id} {{")
            lines.append(f"        string {node_label}")
            lines.append("    }")
        for edge in edges:
            source = self._safe_node_id(edge.source)
            target = self._safe_node_id(edge.target)
            label = sanitize_label(edge.label) if edge.label else "relates_to"
            lines.append(f"    {source} ||--o{{ {target} : {label}")
        return "\n".join(lines)

    def _build_timeline(self, visual_plan: VisualPlan) -> str:
        nodes = visual_plan.diagram_nodes or self._fallback_nodes()
        lines = ["timeline"]
        title = sanitize_label(visual_plan.style.title) if visual_plan.style.title else "Timeline"
        lines.append(f"    title {title}")
        for node in nodes:
            marker = sanitize_label(node.id)
            label = sanitize_label(node.label)
            lines.append(f"    {marker} : {label}")
        return "\n".join(lines)

    def _build_swimlane(self, visual_plan: VisualPlan) -> str:
        nodes = visual_plan.diagram_nodes or self._fallback_nodes()
        edges = visual_plan.diagram_edges or self._fallback_edges(nodes)
        lines = ["flowchart LR"]
        lanes: dict[str, list[DiagramNode]] = {}
        for node in nodes:
            parts = node.label.split(":", 1)
            lane = sanitize_label(parts[0].strip()) if len(parts) > 1 else "Lane"
            lanes.setdefault(lane, []).append(node)
        for lane, lane_nodes in lanes.items():
            lines.append(f"    subgraph {self._safe_node_id(lane)}[{lane}]")
            for node in lane_nodes:
                lines.append(
                    f"        {self._safe_node_id(node.id)}{self._node_brackets(node, visual_plan)}"
                )
            lines.append("    end")
        for edge in edges:
            source = self._safe_node_id(edge.source)
            target = self._safe_node_id(edge.target)
            if edge.label:
                lines.append(f"    {source} -->|{sanitize_label(edge.label)}| {target}")
            else:
                lines.append(f"    {source} --> {target}")
        return "\n".join(lines)

    def _build_network_diagram(self, visual_plan: VisualPlan) -> str:
        nodes = visual_plan.diagram_nodes or self._fallback_nodes()
        edges = visual_plan.diagram_edges or self._fallback_edges(nodes)
        lines = ["flowchart LR"]
        for node in nodes:
            lines.append(
                f"    {self._safe_node_id(node.id)}(({sanitize_label(node.label)}))"
            )
        for edge in edges:
            source = self._safe_node_id(edge.source)
            target = self._safe_node_id(edge.target)
            if edge.label:
                lines.append(f"    {source} ---|{sanitize_label(edge.label)}| {target}")
            else:
                lines.append(f"    {source} --- {target}")
        return "\n".join(lines)

    def _node_brackets(self, node: DiagramNode, plan: VisualPlan | None = None) -> str:
        label = sanitize_label(node.label)
        if node.node_type == "decision":
            base = f"{{{label}}}"
        elif node.node_type in {"start", "end"}:
            base = f"([{label}])"
        else:
            base = f"[{label}]"
        if plan is None:
            return base
        return _3d_node_shape(mermaid_chart_style(plan), base)

    def _safe_node_id(self, node_id: str) -> str:
        return "".join(ch for ch in node_id if ch.isalnum() or ch == "_")

    def _fallback_nodes(self) -> list[DiagramNode]:
        return [
            DiagramNode(id="A", label="Diagram plan created"),
            DiagramNode(
                id="B", label="Detailed node extraction starts in a later sprint"
            ),
        ]

    def _fallback_edges(self, nodes: list[DiagramNode]) -> list[DiagramEdge]:
        if len(nodes) < 2:
            return []
        return [DiagramEdge(source=nodes[0].id, target=nodes[1].id)]
