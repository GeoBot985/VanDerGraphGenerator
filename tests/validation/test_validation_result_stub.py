"""Validation result stub tests."""

from semantic_visual_builder.validation.validation_result import ValidationResult


def test_validation_result_flags_errors() -> None:
    result = ValidationResult()
    result.add_info("info")
    result.add_warning("warning")
    result.add_error("error")

    assert result.is_valid is False
    assert len(result.messages) == 3
