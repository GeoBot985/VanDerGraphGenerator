"""Helpers for building simple diagram plans from process text."""

from __future__ import annotations

import re

from semantic_visual_builder.utils.text_sanitize import sanitize_label

from .visual_plan_schema import DiagramEdge, DiagramNode, VisualPlan


class DiagramPlanBuilder:
    """Build a basic flowchart plan from prose."""

    def build_basic_flowchart(self, message: str) -> VisualPlan:
        message = re.sub(r"^\s*create a flowchart:\s*", "", message, flags=re.IGNORECASE)
        clauses = [part.strip(" .") for part in re.split(r"[.?!]", message) if part.strip()]
        plan = VisualPlan(visual_kind="diagram", intent="show_process", diagram_type="flowchart")
        if not clauses:
            self._add_placeholder(plan)
            return plan

        node_index = 0
        previous_id: str | None = None
        decision_id: str | None = None
        yes_target: str | None = None
        no_target: str | None = None
        seen_labels: set[str] = set()

        for clause in clauses:
            normalized_clause = sanitize_label(clause)
            if normalized_clause.lower() in seen_labels:
                continue
            seen_labels.add(normalized_clause.lower())
            lowered = clause.lower()
            if lowered.startswith("if complete") or lowered.startswith("if incomplete") or lowered.startswith("if approved") or lowered.startswith("if rejected"):
                if decision_id is None:
                    decision_id = self._next_id(node_index)
                    plan.diagram_nodes.append(DiagramNode(id=decision_id, label="Request complete?", node_type="decision"))
                    if previous_id is not None:
                        plan.diagram_edges.append(DiagramEdge(source=previous_id, target=decision_id))
                    node_index += 1
                branch_label = self._branch_label(clause)
                branch_id = self._next_id(node_index)
                node_index += 1
                plan.diagram_nodes.append(DiagramNode(id=branch_id, label=branch_label, node_type="process"))
                if "complete" in lowered or "approved" in lowered:
                    yes_target = branch_id
                else:
                    no_target = branch_id
                continue

            node_id = self._next_id(node_index)
            node_index += 1
            plan.diagram_nodes.append(DiagramNode(id=node_id, label=normalized_clause, node_type="process"))
            if previous_id is not None:
                plan.diagram_edges.append(DiagramEdge(source=previous_id, target=node_id))
            previous_id = node_id

        if decision_id is not None:
            if yes_target is not None:
                plan.diagram_edges.append(DiagramEdge(source=decision_id, target=yes_target, label="Yes"))
            if no_target is not None:
                plan.diagram_edges.append(DiagramEdge(source=decision_id, target=no_target, label="No"))
            elif yes_target is not None:
                plan.diagram_edges.append(DiagramEdge(source=decision_id, target=yes_target, label="No"))

        if not plan.diagram_nodes:
            self._add_placeholder(plan)
        return plan

    def _branch_label(self, clause: str) -> str:
        lowered = clause.lower()
        if lowered.startswith("if complete"):
            return self._action_from_clause(clause, "if complete")
        if lowered.startswith("if incomplete"):
            return self._action_from_clause(clause, "if incomplete")
        if lowered.startswith("if approved"):
            return self._action_from_clause(clause, "if approved")
        if lowered.startswith("if rejected"):
            return self._action_from_clause(clause, "if rejected")
        return clause

    def _action_from_clause(self, clause: str, prefix: str) -> str:
        text = clause[len(prefix) :].lstrip(", :")
        text = sanitize_label(text)
        return text.capitalize() if text else prefix.capitalize()

    def _next_id(self, index: int) -> str:
        return chr(ord("A") + index)

    def _add_placeholder(self, plan: VisualPlan) -> None:
        plan.diagram_nodes.append(DiagramNode(id="A", label="Diagram plan created"))
        plan.diagram_nodes.append(DiagramNode(id="B", label="Detailed node extraction starts in a later sprint"))
        plan.diagram_edges.append(DiagramEdge(source="A", target="B"))
