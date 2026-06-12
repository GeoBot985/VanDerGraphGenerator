"""Build style profiles from extracted image style signals."""

from __future__ import annotations

from datetime import datetime, timezone

from semantic_visual_builder.styles.style_schema import (
    ChartStyle,
    ColourPalette,
    DiagramStyle,
    RendererStyleHints,
    StyleMetadata,
    StyleProfile,
    TypographyStyle,
)
from semantic_visual_builder.image_style.colour_utils import saturation_approx
from semantic_visual_builder.utils.text_sanitize import normalize_name

from .image_metadata import ImageMetadata
from .image_style_analyzer import DeterministicImageStyleAnalysis
from .palette_extractor import PaletteExtractionResult
from .vlm_style_analyzer import VlmStyleAnalysis

_FONT_FAMILY_MAP = {
    "sans-serif": "Arial",
    "serif": "Georgia",
    "monospace": "Courier New",
}


class StyleDraftBuilder:
    def build_style_profile(
        self,
        style_name: str,
        image_metadata: ImageMetadata,
        palette_result: PaletteExtractionResult,
        deterministic_analysis: DeterministicImageStyleAnalysis,
        vlm_analysis: VlmStyleAnalysis | None = None,
    ) -> StyleProfile:
        resolved_name = self._resolve_style_name(
            style_name, deterministic_analysis, vlm_analysis
        )
        style_id = normalize_name(resolved_name) or "extracted_style"
        tags = self._build_tags(deterministic_analysis, vlm_analysis)
        description = (
            "Extracted from an image reference using deterministic palette analysis."
        )
        if vlm_analysis and vlm_analysis.suggested_name:
            description = (
                "Extracted from an image reference with optional VLM style hints."
            )

        # VLM dark-tone overrides deterministic background classification
        is_dark = deterministic_analysis.background_tone == "dark"
        if vlm_analysis and vlm_analysis.inferred_tone == "dark":
            is_dark = True

        # Grid: VLM grid_style takes priority; "minimal" tone forces none
        grid = deterministic_analysis.grid_hint
        if vlm_analysis and vlm_analysis.grid_style is not None:
            grid = vlm_analysis.grid_style
        elif vlm_analysis and vlm_analysis.inferred_tone == "minimal":
            grid = "none"

        # Label density: VLM overrides deterministic when present
        label_density = deterministic_analysis.label_density_hint
        if vlm_analysis and vlm_analysis.label_density is not None:
            label_density = vlm_analysis.label_density

        # Font family: VLM category overrides default
        font_family = "Arial"
        if vlm_analysis and vlm_analysis.font_category:
            font_family = _FONT_FAMILY_MAP.get(vlm_analysis.font_category, "Arial")

        text_hint = deterministic_analysis.text_colour_hint or (
            "#ffffff" if is_dark else "#000000"
        )
        # Sequence: saturation-sorted so data series colours come first
        non_bg = [c for c in palette_result.colours if c.role_hint != "background"]
        non_bg.sort(key=lambda c: saturation_approx(c.rgb), reverse=True)
        sequence_colours = [c.hex_value for c in non_bg[:6]]
        palette = ColourPalette(
            primary=palette_result.primary_colour,
            secondary=palette_result.accent_colour,
            accent=palette_result.accent_colour,
            neutral=palette_result.neutral_colour or (
                "#aaaaaa" if is_dark else "#666666"
            ),
            warning=None,
            success=None,
            danger=None,
            sequence=sequence_colours,
        )
        background = palette_result.background_colour or ("#111111" if is_dark else "#ffffff")
        plot_background = background
        chart = ChartStyle(
            background=background,
            plot_background=plot_background,
            grid=grid,
            legend_position="right",
            label_density=label_density,
            title_alignment="left",
        )
        node_stroke = palette_result.primary_colour or ("#00b0f0" if is_dark else "#1f4e79")
        diagram = DiagramStyle(
            direction="LR" if image_metadata.aspect_ratio >= 1.15 else "TD",
            node_fill=palette_result.primary_colour or background,
            node_stroke=node_stroke,
            decision_fill=palette_result.accent_colour or background,
            edge_colour=node_stroke,
        )
        renderer_hints = RendererStyleHints(
            plotly_template="plotly_dark" if is_dark else "plotly_white",
            mermaid_theme="dark" if is_dark else "base",
        )
        metadata = StyleMetadata(
            style_id=style_id,
            style_name=resolved_name,
            description=description,
            created_at=datetime.now(timezone.utc).isoformat(),
            updated_at=datetime.now(timezone.utc).isoformat(),
            author="image-style-extraction",
            tags=tags,
        )
        return StyleProfile(
            metadata=metadata,
            palette=palette,
            typography=TypographyStyle(font_family=font_family),
            chart=chart,
            diagram=diagram,
            renderer_hints=renderer_hints,
            supported_visual_kinds=["chart", "diagram"],
            supported_renderers=["plotly", "mermaid"],
        )

    def _resolve_style_name(
        self,
        style_name: str,
        deterministic_analysis: DeterministicImageStyleAnalysis,
        vlm_analysis: VlmStyleAnalysis | None,
    ) -> str:
        candidate = style_name.strip()
        if candidate:
            return candidate
        if vlm_analysis and vlm_analysis.suggested_name:
            return vlm_analysis.suggested_name
        tone = deterministic_analysis.chart_tone.replace("_", " ").title()
        return f"Extracted {tone} Style"

    def _build_tags(
        self,
        deterministic_analysis: DeterministicImageStyleAnalysis,
        vlm_analysis: VlmStyleAnalysis | None,
    ) -> list[str]:
        tags = [
            "image-extracted",
            deterministic_analysis.background_tone,
            deterministic_analysis.chart_tone,
            deterministic_analysis.grid_hint,
        ]
        if vlm_analysis is not None:
            tags.extend(vlm_analysis.style_words)
            if vlm_analysis.inferred_tone:
                tags.append(vlm_analysis.inferred_tone)
        return sorted({tag.strip().lower().replace(" ", "-") for tag in tags if tag})
