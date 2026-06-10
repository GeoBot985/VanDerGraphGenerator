"""Plotly renderer placeholder."""

from .base_renderer import BaseRenderer


class PlotlyRenderer(BaseRenderer):
    """Stub Plotly renderer."""

    def can_render(self, visual_plan) -> bool:
        return False

    def render(self, visual_plan, dataset=None):
        return None

    def validate_output(self, output):
        return True
