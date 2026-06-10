"""Helpers for building simple diagram plans from process text."""

from __future__ import annotations

import re

from .visual_plan_schema import DiagramEdge, DiagramNode, VisualPlan


class DiagramPlanBuilder:
    """Build a basic flowchart plan from prose."""

    def build_basic_flowchart(self, message: str) -> VisualPlan:
        sentences = [part.strip(" .") for part in re.split(r"[.?!]", message) if part.strip()]
        plan = VisualPlan(visual_kind="diagram", intent="show_process", diagram_type="flowchart")
        if not sentences:
            plan.diagram_nodes.append(DiagramNode(id="A", label="Diagram plan created"))
            plan.diagram_nodes.append(DiagramNode(id="B", label="Detailed node extraction starts in a later sprint"))
            plan.diagram_edges.append(DiagramEdge(source="A", target="B"))
            return plan

        node_ids = [chr(ord("A") + index) for index in range(len(sentences))]
        previous_id = None
        decision_id = None
        for index, sentence in enumerate(sentences):
            node_id = node_ids[index]
            lowered = sentence.lower()
            is_decision = lowered.startswith("if ") or "if complete" in lowered or "if incomplete" in lowered
            if is_decision and decision_id is None:
                decision_id = node_id
                label = self._decision_label(sentence)
                plan.diagram_nodes.append(DiagramNode(id=node_id, label=label, node_type="decision"))
            elif is_decision:
                plan.diagram_nodes.append(DiagramNode(id=node_id, label=sentence, node_type="process"))
            else:
                plan.diagram_nodes.append(DiagramNode(id=node_id, label=sentence, node_type="process"))
            if previous_id is not None and previous_id != decision_id:
                plan.diagram_edges.append(DiagramEdge(source=previous_id, target=node_id))
            previous_id = node_id

        if decision_id is not None:
            decision_index = node_ids.index(decision_id)
            yes_target = node_ids[decision_index + 1] if decision_index + 1 < len(node_ids) else decision_id
            no_target = node_ids[decision_index + 2] if decision_index + 2 < len(node_ids) else yes_target
            plan.diagram_edges.append(DiagramEdge(source=decision_id, target=yes_target, label="Yes"))
            if no_target != yes_target:
                plan.diagram_edges.append(DiagramEdge(source=decision_id, target=no_target, label="No"))

        return plan

    def _decision_label(self, sentence: str) -> str:
        lowered = sentence.lower()
        if "complete" in lowered:
            return "Request complete?"
        if lowered.startswith("if "):
            return sentence[3:].strip().rstrip(",")
        return sentence
