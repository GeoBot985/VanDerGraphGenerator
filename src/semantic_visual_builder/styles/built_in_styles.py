"""Built-in style profiles."""

from __future__ import annotations

from datetime import datetime, timezone

from .style_schema import (
    ChartStyle,
    ColourPalette,
    DiagramStyle,
    RendererStyleHints,
    StyleMetadata,
    StyleProfile,
    TypographyStyle,
)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _style(
    style_id: str,
    style_name: str,
    description: str,
    tags: list[str],
    *,
    sequence: list[str],
    primary: str | None = None,
    secondary: str | None = None,
    accent: str | None = None,
    neutral: str = "#888888",
    background: str = "#ffffff",
    plot_background: str | None = None,
    grid: str = "light",
    legend_position: str = "right",
    dark: bool = False,
    node_fill: str | None = None,
    node_stroke: str | None = None,
    decision_fill: str | None = None,
    edge_colour: str | None = None,
    font_family: str = "Arial",
) -> StyleProfile:
    """Build a chart+diagram style profile from a colour sequence.

    Diagram colours and renderer hints are derived from the palette so that a
    new theme only needs to specify its distinctive colours.
    """
    primary = primary or sequence[0]
    secondary = secondary or (sequence[1] if len(sequence) > 1 else primary)
    accent = accent or (sequence[2] if len(sequence) > 2 else secondary)
    plot_background = plot_background or background
    node_stroke = node_stroke or primary
    node_fill = node_fill or (primary if dark else "#eeeeee")
    decision_fill = decision_fill or accent
    edge_colour = edge_colour or node_stroke
    return StyleProfile(
        metadata=StyleMetadata(
            style_id=style_id,
            style_name=style_name,
            description=description,
            created_at=_now(),
            tags=tags,
        ),
        palette=ColourPalette(
            primary=primary,
            secondary=secondary,
            accent=accent,
            neutral=neutral,
            sequence=sequence,
        ),
        typography=TypographyStyle(
            font_family=font_family, title_size=18, label_size=12, tick_size=10
        ),
        chart=ChartStyle(
            background=background,
            plot_background=plot_background,
            grid=grid,
            legend_position=legend_position,
            label_density="medium",
            title_alignment="left",
        ),
        diagram=DiagramStyle(
            direction="TD",
            node_fill=node_fill,
            node_stroke=node_stroke,
            decision_fill=decision_fill,
            edge_colour=edge_colour,
        ),
        renderer_hints=RendererStyleHints(
            plotly_template="plotly_dark" if dark else "plotly_white",
            mermaid_theme="dark" if dark else "base",
        ),
        supported_visual_kinds=["chart", "diagram"],
        supported_renderers=["plotly", "mermaid"],
    )


def _additional_style_profiles() -> list[StyleProfile]:
    """Standard colour schemes available out of the box."""
    return [
        _style(
            "dark_slate",
            "Dark Slate",
            "Dark slate background with cool blue-teal accents.",
            ["dark", "cool", "presentation"],
            background="#1e293b",
            grid="none",
            dark=True,
            neutral="#94a3b8",
            sequence=["#38bdf8", "#34d399", "#fbbf24", "#f472b6", "#a78bfa", "#fb7185"],
        ),
        _style(
            "midnight_neon",
            "Midnight Neon",
            "Near-black background with vivid neon data colours.",
            ["dark", "neon", "vibrant"],
            background="#0d1829",
            grid="none",
            dark=True,
            neutral="#64748b",
            sequence=["#ff6d00", "#00e5ff", "#00e676", "#d500f9", "#ffea00", "#ff1744"],
        ),
        _style(
            "vibrant",
            "Vibrant",
            "Bright, high-saturation categorical palette on white.",
            ["vibrant", "categorical", "bright"],
            sequence=["#e6194b", "#3cb44b", "#4363d8", "#f58231", "#911eb4", "#42d4f4"],
        ),
        _style(
            "colorblind_safe",
            "Colorblind Safe",
            "Okabe-Ito colour-vision-deficiency-safe palette.",
            ["accessible", "colorblind", "categorical"],
            primary="#0072b2",
            sequence=["#0072b2", "#e69f00", "#009e73", "#cc79a7", "#56b4e9", "#d55e00"],
        ),
        _style(
            "ocean",
            "Ocean",
            "Sequential ocean blues and teals.",
            ["sequential", "blue", "cool"],
            grid="light",
            sequence=["#023e8a", "#0077b6", "#0096c7", "#00b4d8", "#48cae4", "#90e0ef"],
        ),
        _style(
            "sunset",
            "Sunset",
            "Warm sunset reds, oranges and magentas.",
            ["warm", "sunset", "categorical"],
            sequence=["#ff0054", "#ff5400", "#ff8500", "#ff9e00", "#9e0059", "#390099"],
        ),
        _style(
            "forest",
            "Forest",
            "Earthy greens for natural, organic themes.",
            ["green", "earth", "natural"],
            sequence=["#283618", "#606c38", "#588157", "#3a5a40", "#a3b18a", "#dad7cd"],
        ),
        _style(
            "pastel",
            "Pastel",
            "Soft pastel palette for gentle, approachable visuals.",
            ["pastel", "soft", "light"],
            neutral="#cccccc",
            sequence=["#ffadad", "#ffd6a5", "#caffbf", "#9bf6ff", "#bdb2ff", "#fdffb6"],
        ),
        _style(
            "monochrome_blue",
            "Monochrome Blue",
            "Single-hue sequential blues for ordered data.",
            ["monochrome", "sequential", "blue"],
            sequence=["#08306b", "#2171b5", "#4292c6", "#6baed6", "#9ecae1", "#c6dbef"],
        ),
        _style(
            "high_contrast",
            "High Contrast",
            "Bold high-contrast palette for accessibility and print.",
            ["accessible", "high-contrast", "bold"],
            grid="medium",
            neutral="#555555",
            sequence=["#000000", "#e6194b", "#3cb44b", "#4363d8", "#f58231", "#ffe119"],
        ),
        _style(
            "solarized",
            "Solarized",
            "Solarized accent palette on a warm cream background.",
            ["solarized", "muted", "developer"],
            background="#fdf6e3",
            plot_background="#fdf6e3",
            neutral="#93a1a1",
            sequence=["#268bd2", "#2aa198", "#859900", "#b58900", "#cb4b16", "#d33682"],
        ),
        _style(
            "warm_earth",
            "Warm Earth",
            "Muted autumnal earth tones.",
            ["earth", "autumn", "muted"],
            neutral="#b6ad90",
            sequence=["#582f0e", "#7f4f24", "#936639", "#a68a64", "#b6ad90", "#c2c5aa"],
        ),
    ]


def list_builtin_style_profiles() -> list[StyleProfile]:
    return [
        StyleProfile(
            metadata=StyleMetadata(
                style_id="corporate_blue",
                style_name="Corporate Blue",
                description="Clean corporate style with blue accents.",
                created_at=_now(),
                tags=["corporate", "blue", "presentation"],
            ),
            palette=ColourPalette(
                primary="#1f4e79",
                secondary="#5b9bd5",
                accent="#70ad47",
                neutral="#a5a5a5",
                warning="#ffc000",
                success="#70ad47",
                danger="#c00000",
                sequence=["#1f4e79", "#5b9bd5", "#70ad47", "#a5a5a5"],
            ),
            typography=TypographyStyle(font_family="Arial", title_size=18, label_size=12, tick_size=10),
            chart=ChartStyle(
                background="#ffffff",
                plot_background="#ffffff",
                grid="light",
                legend_position="right",
                label_density="medium",
                title_alignment="left",
            ),
            diagram=DiagramStyle(
                direction="TD",
                node_fill="#d9eaf7",
                node_stroke="#1f4e79",
                decision_fill="#fff2cc",
                edge_colour="#1f4e79",
            ),
            renderer_hints=RendererStyleHints(plotly_template="plotly_white", mermaid_theme="base"),
            supported_visual_kinds=["chart", "diagram"],
            supported_renderers=["plotly", "mermaid"],
        ),
        StyleProfile(
            metadata=StyleMetadata(
                style_id="minimal_grey",
                style_name="Minimal Grey",
                description="Neutral low-colour styling.",
                created_at=_now(),
                tags=["minimal", "grey"],
            ),
            palette=ColourPalette(
                primary="#666666",
                secondary="#999999",
                accent="#444444",
                neutral="#d9d9d9",
                sequence=["#666666", "#999999", "#bbbbbb", "#dddddd"],
            ),
            typography=TypographyStyle(font_family="Arial", title_size=16, label_size=11, tick_size=10),
            chart=ChartStyle(
                background="#f7f7f7",
                plot_background="#ffffff",
                grid="light",
                legend_position="right",
                label_density="medium",
                title_alignment="left",
            ),
            diagram=DiagramStyle(
                direction="TD",
                node_fill="#eeeeee",
                node_stroke="#666666",
                decision_fill="#f5f5f5",
                edge_colour="#666666",
            ),
            renderer_hints=RendererStyleHints(plotly_template="plotly_white", mermaid_theme="base"),
            supported_visual_kinds=["chart", "diagram"],
            supported_renderers=["plotly", "mermaid", "chartjs"],
        ),
        StyleProfile(
            metadata=StyleMetadata(
                style_id="presentation_green",
                style_name="Presentation Green",
                description="Presentation-friendly green highlights.",
                created_at=_now(),
                tags=["presentation", "green"],
            ),
            palette=ColourPalette(
                primary="#2f7d32",
                secondary="#81c784",
                accent="#66bb6a",
                neutral="#bdbdbd",
                sequence=["#2f7d32", "#66bb6a", "#a5d6a7", "#c8e6c9"],
            ),
            typography=TypographyStyle(font_family="Arial", title_size=18, label_size=12, tick_size=10),
            chart=ChartStyle(
                background="#ffffff",
                plot_background="#ffffff",
                grid="light",
                legend_position="bottom",
                label_density="medium",
                title_alignment="left",
            ),
            diagram=DiagramStyle(
                direction="TD",
                node_fill="#e8f5e9",
                node_stroke="#2f7d32",
                decision_fill="#fffde7",
                edge_colour="#2f7d32",
            ),
            renderer_hints=RendererStyleHints(plotly_template="plotly_white", mermaid_theme="base"),
            supported_visual_kinds=["chart", "diagram"],
            supported_renderers=["plotly", "mermaid"],
        ),
        StyleProfile(
            metadata=StyleMetadata(
                style_id="process_blue",
                style_name="Process Blue",
                description="Flowchart and process diagram styling.",
                created_at=_now(),
                tags=["diagram", "process", "blue"],
            ),
            palette=ColourPalette(
                primary="#1f4e79",
                secondary="#5b9bd5",
                accent="#70ad47",
                sequence=["#d9eaf7", "#fff2cc", "#e2f0d9"],
            ),
            typography=TypographyStyle(font_family="Arial", title_size=16, label_size=11, tick_size=10),
            chart=ChartStyle(
                background="#ffffff",
                plot_background="#ffffff",
                grid="none",
                legend_position="none",
                label_density="low",
                title_alignment="left",
            ),
            diagram=DiagramStyle(
                direction="TD",
                node_fill="#d9eaf7",
                node_stroke="#1f4e79",
                decision_fill="#fff2cc",
                edge_colour="#1f4e79",
                class_defs={
                    "process": {
                        "fill": "#d9eaf7",
                        "stroke": "#1f4e79",
                        "color": "#000000",
                    },
                    "decision": {
                        "fill": "#fff2cc",
                        "stroke": "#1f4e79",
                        "color": "#000000",
                    },
                    "start": {
                        "fill": "#e2f0d9",
                        "stroke": "#1f4e79",
                        "color": "#000000",
                    },
                    "end": {
                        "fill": "#fce4d6",
                        "stroke": "#1f4e79",
                        "color": "#000000",
                    },
                },
            ),
            renderer_hints=RendererStyleHints(plotly_template="plotly_white", mermaid_theme="base"),
            supported_visual_kinds=["diagram", "chart"],
            supported_renderers=["mermaid", "plotly"],
        ),
        *_additional_style_profiles(),
    ]
