"""Tests for Plotly style adapter with extracted dark/light styles."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from semantic_visual_builder.renderers.plotly_style_adapter import PlotlyStyleAdapter


def _make_plan(
    background: str | None = None,
    plot_background: str | None = None,
    grid: str | None = None,
    palette: dict | None = None,
    font_family: str | None = None,
) -> MagicMock:
    plan = MagicMock()
    plan.style.title = None
    plan.style.subtitle = None
    plan.style.background = background
    plan.style.plot_background = plot_background
    plan.style.grid = grid
    plan.style.font_family = font_family
    plan.style.legend_position = None
    plan.style.palette = palette or {}
    return plan


class TestPlotlyDarkStyle:
    def setup_method(self) -> None:
        self.adapter = PlotlyStyleAdapter()

    def test_dark_background_sets_dark_bgcolor(self) -> None:
        plan = _make_plan(background="#111111")
        config = self.adapter.apply_style_to_config({"layout": {}}, plan)
        assert config["layout"]["paper_bgcolor"] == "#111111"

    def test_dark_background_sets_white_font_colour(self) -> None:
        plan = _make_plan(background="#111111")
        config = self.adapter.apply_style_to_config({"layout": {}}, plan)
        assert config["layout"]["font"]["color"] == "#ffffff"

    def test_light_background_sets_dark_font_colour(self) -> None:
        plan = _make_plan(background="#ffffff")
        config = self.adapter.apply_style_to_config({"layout": {}}, plan)
        assert config["layout"]["font"]["color"] == "#000000"

    def test_dark_grid_uses_muted_contrast(self) -> None:
        plan = _make_plan(background="#111111", grid="light")
        config = self.adapter.apply_style_to_config({"layout": {}}, plan)
        xaxis = config["layout"].get("xaxis", {})
        assert xaxis.get("showgrid") is True
        gridcolor = xaxis.get("gridcolor", "")
        assert "255" in gridcolor

    def test_grid_none_disables_grid(self) -> None:
        plan = _make_plan(background="#ffffff", grid="none")
        config = self.adapter.apply_style_to_config({"layout": {}}, plan)
        xaxis = config["layout"]["xaxis"]
        assert xaxis["showgrid"] is False

    def test_sequence_palette_applied_as_colorway(self) -> None:
        plan = _make_plan(
            palette={"sequence": ["#1f4e79", "#5b9bd5", "#70ad47"]}
        )
        config = self.adapter.apply_style_to_config({"layout": {}}, plan)
        assert config["layout"]["colorway"] == ["#1f4e79", "#5b9bd5", "#70ad47"]

    def test_primary_secondary_accent_as_colorway_fallback(self) -> None:
        plan = _make_plan(
            palette={"primary": "#1f4e79", "secondary": "#5b9bd5", "accent": "#70ad47"}
        )
        config = self.adapter.apply_style_to_config({"layout": {}}, plan)
        assert "#1f4e79" in config["layout"]["colorway"]

    def test_plot_background_set_separately(self) -> None:
        plan = _make_plan(background="#ffffff", plot_background="#f0f0f0")
        config = self.adapter.apply_style_to_config({"layout": {}}, plan)
        assert config["layout"]["plot_bgcolor"] == "#f0f0f0"
