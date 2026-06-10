"""App state tests."""

from pathlib import Path

from semantic_visual_builder.state.app_state import AppState
from semantic_visual_builder.planning.visual_plan_schema import VisualPlan
from semantic_visual_builder.renderers.renderer_result import RendererOutput


def test_app_state_initializes() -> None:
    state = AppState()
    assert state.ollama_status is None
    assert state.status_messages == []


def test_status_messages_and_selection() -> None:
    state = AppState()
    state.add_status("ready")
    assert state.status_messages == ["ready"]
    state.model_registry.select_model("missing")
    assert state.model_registry.selected_model is None


def test_conversation_messages_append() -> None:
    from semantic_visual_builder.state.conversation_state import ConversationState

    conversation = ConversationState()
    conversation.add_user_message("hello")
    conversation.add_assistant_message("hi")
    assert [message.role for message in conversation.messages] == ["user", "assistant"]


def test_set_visual_plan_clears_preview_state() -> None:
    state = AppState()
    state.last_preview_path = Path("dummy.html")
    state.last_renderer_output = RendererOutput(renderer_name="plotly", output_type="plotly_json", content="{}")
    state.set_visual_plan(VisualPlan(visual_kind="chart", intent="compare_categories"))
    assert state.last_preview_path is None
    assert state.last_renderer_output is None
    assert state.status_messages[-1] == "Visual plan changed. Preview needs regeneration."
