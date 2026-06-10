"""Rule-based message intent classification."""

from __future__ import annotations

from enum import Enum


class MessageIntent(str, Enum):
    CAPABILITY_QUESTION = "capability_question"
    VISUAL_REQUEST = "visual_request"
    REFINEMENT_REQUEST = "refinement_request"
    WORKFLOW_HELP = "workflow_help"
    UNKNOWN = "unknown"


class MessageClassifier:
    """Classify user input into high-level workflow routes."""

    def classify(self, message: str, has_current_plan: bool = False) -> MessageIntent:
        text = message.strip().lower()
        if not text:
            return MessageIntent.UNKNOWN

        capability_markers = (
            "can you",
            "supported",
            "what chart types",
            "what can this app do",
            "do you support",
            "capabilit",
            "flowchart",
            "generated python",
            "graphviz",
            "ppt",
            "powerpoint",
        )
        workflow_markers = ("how do i use", "how does this work", "workflow", "what do i do")
        refinement_markers = ("make it", "change", "update", "title", "highlight", "colour", "color", "use pie", "use bar", "use line")
        visual_markers = ("show ", "create ", "make a ", "make me ", "graph", "chart", "diagram", "plot", "visualize", "per week", "per month", "over time", "by ")

        if any(marker in text for marker in workflow_markers):
            return MessageIntent.WORKFLOW_HELP
        if any(marker in text for marker in capability_markers) and ("?" in text or text.startswith("can you") or text.startswith("what ")):
            return MessageIntent.CAPABILITY_QUESTION
        if has_current_plan and any(marker in text for marker in refinement_markers):
            return MessageIntent.REFINEMENT_REQUEST
        if any(marker in text for marker in visual_markers):
            return MessageIntent.VISUAL_REQUEST
        if has_current_plan and ("bar chart" in text or "line chart" in text or "horizontal" in text):
            return MessageIntent.REFINEMENT_REQUEST
        return MessageIntent.UNKNOWN
