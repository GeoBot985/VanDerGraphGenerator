"""Validation result stubs."""

from dataclasses import dataclass, field
from enum import Enum


class ValidationSeverity(str, Enum):
    """Validation severity levels."""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


@dataclass
class ValidationMessage:
    """Single validation message."""

    severity: ValidationSeverity
    message: str


@dataclass
class ValidationResult:
    """Container for validation messages."""

    messages: list[ValidationMessage] = field(default_factory=list)

    def add_info(self, message: str) -> None:
        self.messages.append(ValidationMessage(ValidationSeverity.INFO, message))

    def add_warning(self, message: str) -> None:
        self.messages.append(ValidationMessage(ValidationSeverity.WARNING, message))

    def add_error(self, message: str) -> None:
        self.messages.append(ValidationMessage(ValidationSeverity.ERROR, message))

    @property
    def is_valid(self) -> bool:
        return not any(item.severity == ValidationSeverity.ERROR for item in self.messages)
