"""Conversation state helpers."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class ConversationMessage:
    role: str
    content: str


@dataclass
class ConversationState:
    messages: list[ConversationMessage] = field(default_factory=list)

    def add_user_message(self, content: str) -> None:
        self.messages.append(ConversationMessage(role="user", content=content))

    def add_assistant_message(self, content: str) -> None:
        self.messages.append(ConversationMessage(role="assistant", content=content))

    def clear(self) -> None:
        self.messages.clear()
