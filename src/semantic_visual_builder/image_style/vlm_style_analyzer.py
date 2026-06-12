"""Optional VLM-backed image style analysis."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from semantic_visual_builder.llm.llm_response_parser import LlmResponseParser
from semantic_visual_builder.llm.ollama_client import OllamaClient

from .image_style_analyzer import DeterministicImageStyleAnalysis
from .image_style_prompts import IMAGE_STYLE_ANALYSIS_SYSTEM_PROMPT
from .vision_model_detector import VisionModelDetector

_ALLOWED_TONES = {"corporate", "presentation", "minimal", "technical", "playful", "dark", "neutral", "report"}
_ALLOWED_GRID = {"none", "light", "medium"}
_ALLOWED_DENSITY = {"low", "medium", "high"}
_ALLOWED_FONT_CAT = {"sans-serif", "serif", "monospace"}


@dataclass
class VlmStyleAnalysis:
    raw_response: str
    parsed_json: dict | None
    style_words: list[str] = field(default_factory=list)
    inferred_tone: str | None = None
    suggested_name: str | None = None
    font_category: str | None = None
    grid_style: str | None = None
    label_density: str | None = None
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


class VlmStyleAnalyzer:
    def __init__(
        self,
        ollama_client: OllamaClient,
        response_parser: LlmResponseParser | None = None,
        vision_detector: VisionModelDetector | None = None,
    ):
        self.ollama_client = ollama_client
        self.response_parser = response_parser or LlmResponseParser()
        self.vision_detector = vision_detector or VisionModelDetector()

    def analyze_image_style(
        self,
        model: str,
        image_path: Path,
        deterministic_analysis: DeterministicImageStyleAnalysis,
        skip_vision_check: bool = False,
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
        warnings: list[str] = []
        if (
            not skip_vision_check
            and not self.vision_detector.is_likely_vision_model(model)
        ):
            warnings.append(
                f"Model '{model}' is not tagged as vision-capable by the local "
                "heuristic. Attempting image input anyway."
            )
        try:
            raw_response = generate_vision(
                model=model,
                image_path=image_path,
                prompt=prompt,
                system=IMAGE_STYLE_ANALYSIS_SYSTEM_PROMPT,
            )
        except Exception as exc:
            return VlmStyleAnalysis(
                raw_response="",
                parsed_json=None,
                warnings=warnings,
                errors=[str(exc)],
            )

        try:
            parsed = self.response_parser.parse_json_response(raw_response)
        except Exception as exc:
            return VlmStyleAnalysis(
                raw_response=raw_response,
                parsed_json=None,
                warnings=warnings + ["Vision output could not be parsed as JSON."],
                errors=[str(exc)],
            )

        raw_tone = parsed.get("inferred_tone")
        inferred_tone: str | None = None
        if isinstance(raw_tone, str):
            cleaned = raw_tone.strip().lower()
            if cleaned in _ALLOWED_TONES:
                inferred_tone = cleaned
            else:
                warnings.append(
                    f"VLM inferred_tone '{raw_tone}' is not a recognised value; ignored."
                )

        raw_font = parsed.get("font_category")
        font_category: str | None = None
        if isinstance(raw_font, str):
            cleaned = raw_font.strip().lower()
            if cleaned in _ALLOWED_FONT_CAT:
                font_category = cleaned
            else:
                warnings.append(f"VLM font_category '{raw_font}' is not recognised; ignored.")

        raw_grid = parsed.get("grid_style")
        grid_style: str | None = None
        if isinstance(raw_grid, str):
            cleaned = raw_grid.strip().lower()
            if cleaned in _ALLOWED_GRID:
                grid_style = cleaned
            else:
                warnings.append(f"VLM grid_style '{raw_grid}' is not recognised; ignored.")

        raw_density = parsed.get("label_density")
        label_density: str | None = None
        if isinstance(raw_density, str):
            cleaned = raw_density.strip().lower()
            if cleaned in _ALLOWED_DENSITY:
                label_density = cleaned
            else:
                warnings.append(f"VLM label_density '{raw_density}' is not recognised; ignored.")

        return VlmStyleAnalysis(
            raw_response=raw_response,
            parsed_json=parsed,
            style_words=[
                str(item)
                for item in parsed.get("style_words", [])
                if isinstance(item, str)
            ],
            inferred_tone=inferred_tone,
            suggested_name=parsed.get("suggested_name")
            if isinstance(parsed.get("suggested_name"), str)
            else None,
            font_category=font_category,
            grid_style=grid_style,
            label_density=label_density,
            warnings=warnings,
        )
