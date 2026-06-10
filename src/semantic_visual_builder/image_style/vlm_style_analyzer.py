"""Optional VLM-backed image style analysis."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from semantic_visual_builder.llm.llm_response_parser import LlmResponseParser
from semantic_visual_builder.llm.ollama_client import OllamaClient

from .image_style_analyzer import DeterministicImageStyleAnalysis
from .image_style_prompts import IMAGE_STYLE_ANALYSIS_SYSTEM_PROMPT


@dataclass
class VlmStyleAnalysis:
    raw_response: str
    parsed_json: dict | None
    style_words: list[str] = field(default_factory=list)
    inferred_tone: str | None = None
    suggested_name: str | None = None
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


class VlmStyleAnalyzer:
    def __init__(
        self,
        ollama_client: OllamaClient,
        response_parser: LlmResponseParser | None = None,
    ):
        self.ollama_client = ollama_client
        self.response_parser = response_parser or LlmResponseParser()

    def analyze_image_style(
        self,
        model: str,
        image_path: Path,
        deterministic_analysis: DeterministicImageStyleAnalysis,
    ) -> VlmStyleAnalysis:
        generate_vision = getattr(self.ollama_client, "generate_vision", None)
        if not callable(generate_vision):
            return VlmStyleAnalysis(
                raw_response="",
                parsed_json=None,
                warnings=[
                    "Vision-capable Ollama image input is not available; "
                    "deterministic extraction was used."
                ],
            )

        prompt = (
            f"{IMAGE_STYLE_ANALYSIS_SYSTEM_PROMPT}\n"
            f"Deterministic hints:\n"
            f"- background: {deterministic_analysis.background_tone}\n"
            f"- contrast: {deterministic_analysis.contrast_level}\n"
            f"- chart tone: {deterministic_analysis.chart_tone}\n"
            f"- grid: {deterministic_analysis.grid_hint}\n"
            f"- label density: {deterministic_analysis.label_density_hint}\n"
        )
        try:
            raw_response = generate_vision(
                model=model,
                image_path=image_path,
                prompt=prompt,
                system=IMAGE_STYLE_ANALYSIS_SYSTEM_PROMPT,
            )
        except NotImplementedError as exc:
            return VlmStyleAnalysis(
                raw_response="",
                parsed_json=None,
                warnings=[str(exc)],
            )
        except Exception as exc:
            return VlmStyleAnalysis(
                raw_response="",
                parsed_json=None,
                errors=[str(exc)],
            )

        try:
            parsed = self.response_parser.parse_json_response(raw_response)
        except Exception as exc:
            return VlmStyleAnalysis(
                raw_response=raw_response,
                parsed_json=None,
                warnings=["Vision output could not be parsed as JSON."],
                errors=[str(exc)],
            )

        return VlmStyleAnalysis(
            raw_response=raw_response,
            parsed_json=parsed,
            style_words=[
                str(item)
                for item in parsed.get("style_words", [])
                if isinstance(item, str)
            ],
            inferred_tone=parsed.get("inferred_tone")
            if isinstance(parsed.get("inferred_tone"), str)
            else None,
            suggested_name=parsed.get("suggested_name")
            if isinstance(parsed.get("suggested_name"), str)
            else None,
        )
