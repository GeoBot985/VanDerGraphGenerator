"""Style extraction panel helpers."""

from __future__ import annotations

from semantic_visual_builder.state.app_state import AppState


class StyleExtractionPanel:
    def image_text(self, app_state: AppState) -> str:
        lines = ["Selected image: none"]
        if app_state.selected_style_image_path is not None:
            lines[0] = f"Selected image: {app_state.selected_style_image_path}"
        result = app_state.last_style_extraction_result
        if result is not None and result.image_metadata is not None:
            meta = result.image_metadata
            lines.extend(
                [
                    f"Format: {meta.format or 'unknown'}",
                    f"Size: {meta.width} x {meta.height}",
                    f"Mode: {meta.mode}",
                    f"Aspect ratio: {meta.aspect_ratio:.2f}",
                ]
            )
        return "\n".join(lines)

    def summary_text(self, app_state: AppState) -> str:
        result = app_state.last_style_extraction_result
        if result is None:
            return "No style extracted yet."
        lines = [
            f"Style extraction success: {'yes' if result.success else 'no'}",
        ]
        if result.style_profile is not None:
            lines.append(f"Suggested style: {result.style_profile.style_name}")
            lines.append(f"Style ID: {result.style_profile.style_id}")
        if result.deterministic_analysis is not None:
            analysis = result.deterministic_analysis
            lines.extend(
                [
                    f"Background tone: {analysis.background_tone}",
                    f"Contrast level: {analysis.contrast_level}",
                    f"Chart tone: {analysis.chart_tone}",
                    f"Grid hint: {analysis.grid_hint}",
                    f"Label density: {analysis.label_density_hint}",
                ]
            )
        if result.palette_result is not None:
            palette = result.palette_result
            lines.append("Palette:")
            if palette.background_colour:
                lines.append(f"- Background: {palette.background_colour}")
            if palette.primary_colour:
                lines.append(f"- Primary: {palette.primary_colour}")
            if palette.accent_colour:
                lines.append(f"- Accent: {palette.accent_colour}")
            if palette.neutral_colour:
                lines.append(f"- Neutral: {palette.neutral_colour}")
            for colour in palette.colours[:5]:
                lines.append(
                    f"- {colour.hex_value} ({colour.percentage:.1f}%)"
                )
        if result.warnings:
            lines.append("Warnings:")
            lines.extend(f"- {warning}" for warning in result.warnings)
        if result.errors:
            lines.append("Errors:")
            lines.extend(f"- {error}" for error in result.errors)
        return "\n".join(lines)
