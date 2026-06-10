"""Workflow state machine for guided visual building."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class WorkflowStep(str, Enum):
    START = "start"
    DATA_REQUIRED = "data_required"
    DATA_VERIFIED = "data_verified"
    VISUAL_GOAL_REQUIRED = "visual_goal_required"
    GRAPH_TYPE_SELECTED = "graph_type_selected"
    FIELD_MAPPING_CONFIRMED = "field_mapping_confirmed"
    STYLE_OPTIONAL = "style_optional"
    PLAN_READY = "plan_ready"
    REFINEMENT_LOOP = "refinement_loop"
    EXPORT_READY = "export_ready"


@dataclass
class WorkflowState:
    """Track the current guided workflow step."""

    current_step: WorkflowStep = WorkflowStep.START

    def advance_to(self, step: WorkflowStep) -> None:
        self.current_step = step

    def requires_dataset(self) -> bool:
        return self.current_step in {WorkflowStep.START, WorkflowStep.DATA_REQUIRED}

    def allows_visual_request(self) -> bool:
        return self.current_step in {
            WorkflowStep.DATA_VERIFIED,
            WorkflowStep.VISUAL_GOAL_REQUIRED,
            WorkflowStep.GRAPH_TYPE_SELECTED,
            WorkflowStep.FIELD_MAPPING_CONFIRMED,
            WorkflowStep.STYLE_OPTIONAL,
            WorkflowStep.PLAN_READY,
            WorkflowStep.REFINEMENT_LOOP,
            WorkflowStep.EXPORT_READY,
        }

    def allows_refinement(self) -> bool:
        return self.current_step in {
            WorkflowStep.PLAN_READY,
            WorkflowStep.REFINEMENT_LOOP,
            WorkflowStep.EXPORT_READY,
        }
