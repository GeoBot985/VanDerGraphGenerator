"""Base renderer contract placeholder."""


class BaseRenderer:
    def can_render(self, visual_plan) -> bool:
        raise NotImplementedError

    def render(self, visual_plan, dataset=None):
        raise NotImplementedError

    def validate_output(self, output):
        raise NotImplementedError
