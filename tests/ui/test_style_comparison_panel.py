"""Tests for StyleComparisonPanel logic."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from semantic_visual_builder.state.app_state import AppState
from semantic_visual_builder.styles.style_comparison import StyleComparisonResult
from semantic_visual_builder.ui.style_comparison_panel import StyleComparisonPanel


def _make_result(
    style_id: str,
    style_name: str,
    score: float,
    reasons: list[str] | None = None,
) -> StyleComparisonResult:
    return StyleComparisonResult(
        compared_style_id=style_id,
        compared_style_name=style_name,
        similarity_score=score,
        reasons=reasons or [],
    )


class TestStyleComparisonPanel:
    def setup_method(self) -> None:
        self.panel = StyleComparisonPanel()

    def test_no_results_returns_placeholder(self) -> None:
        state = AppState()
        text = self.panel.comparison_text(state)
        assert "No comparison results" in text

    def test_results_sorted_by_score_descending(self) -> None:
        state = AppState()
        state.style_comparison_results = [
            _make_result("b", "B Style", 0.46),
            _make_result("a", "A Style", 0.82),
        ]
        text = self.panel.comparison_text(state)
        pos_a = text.index("A Style")
        pos_b = text.index("B Style")
        assert pos_a < pos_b

    def test_top_match_text_shows_best(self) -> None:
        state = AppState()
        state.style_comparison_results = [
            _make_result("best", "Best Style", 0.88),
            _make_result("worse", "Worse Style", 0.40),
        ]
        text = self.panel.top_match_text(state)
        assert "Best Style" in text

    def test_similarity_percent_displayed(self) -> None:
        state = AppState()
        state.style_comparison_results = [
            _make_result("s", "S", 0.82, reasons=["similar primary"]),
        ]
        text = self.panel.comparison_text(state)
        assert "82%" in text

    def test_can_replace_user_style(self) -> None:
        state = AppState()
        result = _make_result("user_style_abc", "User Style", 0.7)
        assert self.panel.can_replace(result, state) is True

    def test_cannot_replace_builtin_style(self) -> None:
        state = AppState()
        result = _make_result("corporate_blue", "Corporate Blue", 0.9)
        assert self.panel.can_replace(result, state) is False
