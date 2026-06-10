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
from semantic_visual_builder.utils.text_sanitize import normalize_name

from .image_metadata import ImageMetadata
from .image_style_analyzer import DeterministicImageStyleAnalysis
from .palette_extractor import PaletteExtractionResult
from .vlm_style_analyzer import VlmStyleAnalysis


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

        palette = ColourPalette(
            primary=palette_result.primary_colour,
            secondary=palette_result.accent_colour,
            accent=palette_result.accent_colour,
            neutral=palette_result.neutral_colour,
            warning=None,
            success=None,
            danger=None,
            sequence=[colour.hex_value for colour in palette_result.colours[:6]],
        )
        background = palette_result.background_colour or "#ffffff"
        chart = ChartStyle(
            background=background,
            plot_background=background,
            grid=deterministic_analysis.grid_hint,
            legend_position="right",
            label_density=deterministic_analysis.label_density_hint,
            title_alignment="left",
        )
        diagram = DiagramStyle(
            direction="LR" if image_metadata.aspect_ratio >= 1.15 else "TD",
            node_fill=palette_result.primary_colour or background,
            node_stroke=palette_result.primary_colour or "#1f4e79",
            decision_fill=palette_result.accent_colour or background,
            edge_colour=palette_result.primary_colour or "#1f4e79",
        )
        renderer_hints = RendererStyleHints(
            plotly_template="plotly_white"
            if deterministic_analysis.background_tone != "dark"
            else "plotly_dark",
            mermaid_theme="base",
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
            typography=TypographyStyle(font_family="Arial"),
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
