"""Request-level semantic trace metadata."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class SemanticTrace:
    request_id: str
    created_at: str
    user_message: str

    input_interpreter: str
    llm_enabled: bool
    llm_attempted: bool
    llm_model: str | None
    llm_success: bool
    llm_error: str | None = None

    mapping_method: str | None = None
    used_fallback: bool = False
    fallback_reason: str | None = None

    graph_matrix_schema_version: str | None = None
    validation_success: bool = False
    validation_errors: list[str] = field(default_factory=list)
    validation_warnings: list[str] = field(default_factory=list)

    action: str | None = None
    visual_kind: str | None = None
    chart_type: str | None = None
    diagram_type: str | None = None
    renderer: str | None = None

    assumptions: list[str] = field(default_factory=list)
    pending_questions: list[str] = field(default_factory=list)

    raw_llm_response_available: bool = False
    raw_llm_response_preview: str | None = None

    def to_lines(self) -> list[str]:
        lines = [
            f"Request ID: {self.request_id}",
            f"Created at: {self.created_at}",
            f"Input interpreter: {self.input_interpreter}",
            f"LLM enabled: {'yes' if self.llm_enabled else 'no'}",
            f"LLM attempted: {'yes' if self.llm_attempted else 'no'}",
            f"LLM model: {self.llm_model or 'None'}",
            f"LLM success: {'yes' if self.llm_success else 'no'}",
            f"LLM error: {self.llm_error or 'None'}",
            f"Mapping method: {self.mapping_method or 'None'}",
            f"Fallback used: {'yes' if self.used_fallback else 'no'}",
            f"Fallback reason: {self.fallback_reason or 'None'}",
            f"Graph matrix version: {self.graph_matrix_schema_version or 'None'}",
            f"Validation success: {'yes' if self.validation_success else 'no'}",
            f"Action: {self.action or 'None'}",
            f"Visual kind: {self.visual_kind or 'None'}",
            f"Chart type: {self.chart_type or 'None'}",
            f"Diagram type: {self.diagram_type or 'None'}",
            f"Renderer: {self.renderer or 'None'}",
        ]
        raw_available = "yes" if self.raw_llm_response_available else "no"
        lines.append(f"Raw LLM response available: {raw_available}")
        if self.validation_errors:
            lines.append("Validation errors:")
            lines.extend(f"- {message}" for message in self.validation_errors)
        if self.validation_warnings:
            lines.append("Validation warnings:")
            lines.extend(f"- {message}" for message in self.validation_warnings)
        if self.assumptions:
            lines.append("Assumptions:")
            lines.extend(f"- {message}" for message in self.assumptions)
        if self.pending_questions:
            lines.append("Pending questions:")
            lines.extend(f"- {message}" for message in self.pending_questions)
        if self.raw_llm_response_preview:
            lines.append("Raw LLM response preview:")
            lines.append(self.raw_llm_response_preview)
        return lines
