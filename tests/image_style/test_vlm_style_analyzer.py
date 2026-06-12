"""VLM style analyzer tests."""

from pathlib import Path

from semantic_visual_builder.llm.ollama_client import OllamaGenerationError
from semantic_visual_builder.image_style.image_style_analyzer import (
    DeterministicImageStyleAnalysis,
)
from semantic_visual_builder.image_style.palette_extractor import (
    PaletteExtractionResult,
)
from semantic_visual_builder.image_style.vlm_style_analyzer import VlmStyleAnalyzer


class FakeVisionClient:
    def __init__(self, response: str):
        self.response = response

    def generate_vision(self, model, image_path, prompt, system=None):  # noqa: ANN001
        return self.response


class RaisingVisionClient:
    def generate_vision(self, model, image_path, prompt, system=None):  # noqa: ANN001
        raise OllamaGenerationError("vision unsupported")


def _analysis() -> DeterministicImageStyleAnalysis:
    return DeterministicImageStyleAnalysis(
        palette=PaletteExtractionResult(background_colour="#ffffff"),
        background_tone="light",
        contrast_level="medium",
        chart_tone="corporate",
        grid_hint="light",
        label_density_hint="medium",
    )


def test_vlm_analyzer_parses_valid_json(tmp_path: Path) -> None:
    client = FakeVisionClient(
        (
            '{"suggested_name":"Corporate Blue Report",'
            '"style_words":["corporate","blue"],'
            '"inferred_tone":"corporate"}'
        )
    )
    analyzer = VlmStyleAnalyzer(client)

    result = analyzer.analyze_image_style(
        "vision-model", tmp_path / "sample.png", _analysis()
    )

    assert result.parsed_json is not None
    assert result.suggested_name == "Corporate Blue Report"
    assert "corporate" in result.style_words


def test_vlm_analyzer_handles_invalid_json(tmp_path: Path) -> None:
    client = FakeVisionClient("not json")
    analyzer = VlmStyleAnalyzer(client)

    result = analyzer.analyze_image_style(
        "vision-model", tmp_path / "sample.png", _analysis()
    )

    assert result.parsed_json is None
    assert result.errors


def test_vlm_analyzer_warns_when_vision_is_unavailable(tmp_path: Path) -> None:
    analyzer = VlmStyleAnalyzer(object())  # type: ignore[arg-type]

    result = analyzer.analyze_image_style(
        "vision-model", tmp_path / "sample.png", _analysis()
    )

    assert result.parsed_json is None
    assert result.warnings


def test_vlm_analyzer_attempts_unknown_model_anyway(tmp_path: Path) -> None:
    client = FakeVisionClient(
        (
            '{"suggested_name":"Corporate Blue Report",'
            '"style_words":["corporate","blue"],'
            '"inferred_tone":"corporate"}'
        )
    )
    analyzer = VlmStyleAnalyzer(client)

    result = analyzer.analyze_image_style(
        "gemma4:12b-it-qat", tmp_path / "sample.png", _analysis()
    )

    assert result.parsed_json is not None
    assert any("Attempting image input anyway" in warning for warning in result.warnings)


def test_vlm_analyzer_reports_runtime_vision_error_for_unknown_model(tmp_path: Path) -> None:
    analyzer = VlmStyleAnalyzer(RaisingVisionClient())

    result = analyzer.analyze_image_style(
        "gemma4:12b-it-qat", tmp_path / "sample.png", _analysis()
    )

    assert result.parsed_json is None
    assert any("Attempting image input anyway" in warning for warning in result.warnings)
    assert result.errors == ["vision unsupported"]


def test_vlm_analyzer_extracts_font_category(tmp_path: Path) -> None:
    client = FakeVisionClient(
        '{"inferred_tone":"technical","suggested_name":"Mono Tech",'
        '"style_words":["technical"],"font_category":"monospace",'
        '"grid_style":"light","label_density":"high"}'
    )
    analyzer = VlmStyleAnalyzer(client)

    result = analyzer.analyze_image_style(
        "vision-model", tmp_path / "sample.png", _analysis()
    )

    assert result.font_category == "monospace"
    assert result.grid_style == "light"
    assert result.label_density == "high"


def test_vlm_analyzer_ignores_invalid_font_category(tmp_path: Path) -> None:
    client = FakeVisionClient(
        '{"inferred_tone":"corporate","style_words":[],"font_category":"comic-sans"}'
    )
    analyzer = VlmStyleAnalyzer(client)

    result = analyzer.analyze_image_style(
        "vision-model", tmp_path / "sample.png", _analysis()
    )

    assert result.font_category is None
    assert any("font_category" in w for w in result.warnings)
