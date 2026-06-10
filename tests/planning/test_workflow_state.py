"""Workflow state tests."""

from semantic_visual_builder.planning.workflow_state import WorkflowState, WorkflowStep


def test_default_state_is_start() -> None:
    assert WorkflowState().current_step == WorkflowStep.START


def test_advance_to_data_required() -> None:
    state = WorkflowState()
    state.advance_to(WorkflowStep.DATA_REQUIRED)
    assert state.current_step == WorkflowStep.DATA_REQUIRED


def test_allows_visual_request_after_data_verified() -> None:
    state = WorkflowState(current_step=WorkflowStep.DATA_VERIFIED)
    assert state.allows_visual_request() is True


def test_allows_refinement_after_plan_ready() -> None:
    state = WorkflowState(current_step=WorkflowStep.PLAN_READY)
    assert state.allows_refinement() is True
