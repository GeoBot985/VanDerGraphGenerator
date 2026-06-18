"""Validation panel helpers."""

from __future__ import annotations

from semantic_visual_builder.state.app_state import AppState
from semantic_visual_builder.validation.validation_result import ValidationSeverity


class ValidationPanel:
    """Format validation results into grouped text."""

    def validation_text(self, app_state: AppState) -> str:
        validation = app_state.current_validation_result
        if validation is None:
            return "No validation result yet."
        buckets: dict[ValidationSeverity, list[str]] = {
            ValidationSeverity.ERROR: [],
            ValidationSeverity.WARNING: [],
            ValidationSeverity.INFO: [],
        }
        for message in validation.messages:
            buckets[message.severity].append(message.message)
        lines = [f"Plan status: {self.plan_status_text(app_state)}", "", "Errors:"]
        if buckets[ValidationSeverity.ERROR]:
            lines.extend(f"- {message}" for message in buckets[ValidationSeverity.ERROR])
        else:
            lines.append("- None")
        lines.extend(["", "Warnings:"])
        if buckets[ValidationSeverity.WARNING]:
            lines.extend(f"- {message}" for message in buckets[ValidationSeverity.WARNING])
        else:
            lines.append("- None")
        lines.extend(["", "Info:"])
        if buckets[ValidationSeverity.INFO]:
            lines.extend(f"- {message}" for message in buckets[ValidationSeverity.INFO])
        else:
            lines.append("- None")
        return "\n".join(lines)

    def plan_status_text(self, app_state: AppState) -> str:
        if app_state.current_visual_plan is None:
            return "No plan"
        if app_state.current_validation_result is None or not app_state.current_validation_result.is_valid:
            return "Invalid"
        if app_state.current_visual_plan.metadata.is_preview_stale:
            return "Valid, preview stale"
        return "Valid, preview ready"
