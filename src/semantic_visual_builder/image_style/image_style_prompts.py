"""Prompts for optional image style analysis."""

IMAGE_STYLE_ANALYSIS_SYSTEM_PROMPT = """
You analyze the visual style of a chart or diagram image.

Return JSON only with exactly these fields:
{
  "inferred_tone": one of "corporate" | "presentation" | "minimal" | "technical" | "playful" | "dark" | "neutral" | "report",
  "suggested_name": short descriptive name for this style (e.g. "Dark Corporate Blue"),
  "style_words": list of 2-5 adjectives describing the visual style,
  "font_category": one of "sans-serif" | "serif" | "monospace" | null,
  "grid_style": one of "none" | "light" | "medium" | null,
  "label_density": one of "low" | "medium" | "high" | null
}

Do not describe the data values.
Do not recreate the chart.
Do not generate Python, JavaScript, or Mermaid.
Focus only on visual styling: colours, typography, grid density, layout, and presentation tone.
"""
