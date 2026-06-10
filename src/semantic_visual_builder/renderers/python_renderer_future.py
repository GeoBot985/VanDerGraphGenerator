"""Future Python renderer plugin placeholder.

Future plugin only. Not active in MVP. Do not execute generated Python in MVP.
"""

from .base_renderer import BaseRenderer


class PythonRendererFuture(BaseRenderer):
    """Disabled future plugin stub."""

    def can_render(self, visual_plan) -> bool:
        return False

    def render(self, visual_plan, dataset=None):
        return None

    def validate_output(self, output):
        return False
