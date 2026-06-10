"""App state tests."""

from semantic_visual_builder.state.app_state import AppState


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
