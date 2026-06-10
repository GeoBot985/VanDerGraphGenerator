"""Style manager dialog helpers."""

from __future__ import annotations

from dataclasses import dataclass, field

from semantic_visual_builder.styles.style_schema import StyleProfile


@dataclass
class StyleManagerDialogModel:
    available_styles: list[StyleProfile] = field(default_factory=list)
    selected_style_id: str | None = None

    def summary(self) -> str:
        selected = self.selected_style
        if selected is None:
            return "No style selected."
        return f"{selected.style_name}\n{selected.metadata.description or ''}".strip()

    @property
    def selected_style(self) -> StyleProfile | None:
        if self.selected_style_id is None:
            return None
        for style in self.available_styles:
            if style.style_id == self.selected_style_id:
                return style
        return None
