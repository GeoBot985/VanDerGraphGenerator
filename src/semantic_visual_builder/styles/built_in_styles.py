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
    ]
