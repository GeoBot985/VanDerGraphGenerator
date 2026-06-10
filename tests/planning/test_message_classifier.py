"""Message classifier tests."""

from semantic_visual_builder.planning.message_classifier import MessageClassifier, MessageIntent


def test_flowchart_question_is_capability_question() -> None:
    assert MessageClassifier().classify("Can you do flowcharts?") == MessageIntent.CAPABILITY_QUESTION


def test_visual_request_is_classified() -> None:
    assert MessageClassifier().classify("Show transactions per week") == MessageIntent.VISUAL_REQUEST


def test_refinement_request_with_plan() -> None:
    assert MessageClassifier().classify("Make it a bar chart", has_current_plan=True) == MessageIntent.REFINEMENT_REQUEST


def test_workflow_help() -> None:
    assert MessageClassifier().classify("How do I use this?") == MessageIntent.WORKFLOW_HELP
