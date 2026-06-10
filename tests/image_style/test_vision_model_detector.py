"""Tests for VisionModelDetector."""

from __future__ import annotations

import pytest

from semantic_visual_builder.image_style.vision_model_detector import VisionModelDetector


class TestVisionModelDetector:
    def setup_method(self) -> None:
        self.detector = VisionModelDetector()

    def test_llava_detected(self) -> None:
        assert self.detector.is_likely_vision_model("llava:13b") is True

    def test_moondream_detected(self) -> None:
        assert self.detector.is_likely_vision_model("moondream:latest") is True

    def test_qwen_vl_detected(self) -> None:
        assert self.detector.is_likely_vision_model("qwen-vl:7b") is True

    def test_qwen25vl_detected(self) -> None:
        assert self.detector.is_likely_vision_model("qwen2.5vl:7b") is True

    def test_bakllava_detected(self) -> None:
        assert self.detector.is_likely_vision_model("bakllava:latest") is True

    def test_gemma3_detected(self) -> None:
        assert self.detector.is_likely_vision_model("gemma3:4b") is True

    def test_minicpm_v_detected(self) -> None:
        assert self.detector.is_likely_vision_model("minicpm-v:latest") is True

    def test_ordinary_text_model_not_detected(self) -> None:
        assert self.detector.is_likely_vision_model("mistral:7b") is False

    def test_llama3_not_detected(self) -> None:
        assert self.detector.is_likely_vision_model("llama3:8b") is False

    def test_phi3_not_detected(self) -> None:
        assert self.detector.is_likely_vision_model("phi3:latest") is False

    def test_case_insensitive(self) -> None:
        assert self.detector.is_likely_vision_model("LLaVA:latest") is True

    def test_filter_list(self) -> None:
        models = ["llava:13b", "mistral:7b", "moondream", "phi3"]
        vision = self.detector.get_vision_capable_models(models)
        assert "llava:13b" in vision
        assert "moondream" in vision
        assert "mistral:7b" not in vision
        assert "phi3" not in vision

    def test_empty_list_returns_empty(self) -> None:
        assert self.detector.get_vision_capable_models([]) == []
