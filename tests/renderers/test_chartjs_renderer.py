"""Chart.js renderer tests."""

import pytest

from semantic_visual_builder.renderers.chartjs_renderer import ChartJsRenderer


def test_can_render_returns_false_by_default() -> None:
    assert ChartJsRenderer().can_render(object()) is False


def test_render_raises_not_implemented_error() -> None:
    with pytest.raises(NotImplementedError):
        ChartJsRenderer().render(object())
