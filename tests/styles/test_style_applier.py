"""Style applier tests."""

from semantic_visual_builder.planning.visual_plan_schema import VisualPlan
from semantic_visual_builder.styles.style_applier import StyleApplier
from semantic_visual_builder.styles.style_schema import (
    ChartStyle,
    ColourPalette,
    DiagramStyle,
    StyleMetadata,
    StyleProfile,
    TypographyStyle,
)


def _chart_plan() -> VisualPlan:
    return VisualPlan(visual_kind="chart", intent="compare")


def _style() -> StyleProfile:
    style = StyleProfile(
        metadata=StyleMetadata(style_id="corporate_blue", style_name="Corporate Blue"),
        palette=ColourPalette(primary="#1f4e79", secondary="#5b9bd5", accent="#70ad47"),
        typography=TypographyStyle(font_family="Arial"),
        chart=ChartStyle(
            background="#ffffff",
            plot_background="#f7f7f7",
            grid="light",
            legend_position="bottom",
        ),
        diagram=DiagramStyle(
            direction="LR", node_fill="#d9eaf7", node_stroke="#1f4e79"
        ),
    )
    style.diagram.class_defs = {
        "process": {"fill": "#d9eaf7", "stroke": "#1f4e79", "color": "#000000"}
    }
    return style


def test_style_applier_updates_visual_plan_in_place() -> None:
    plan = _chart_plan()

    result = StyleApplier().apply_style(plan, _style())

    assert result.success is True
    assert result.visual_plan is plan
    assert plan.metadata.style_profile_id == "corporate_blue"
    assert plan.metadata.style_profile_name == "Corporate Blue"
    assert plan.style.font_family == "Arial"
    assert plan.style.background == "#ffffff"
    assert plan.style.legend_position == "bottom"
    assert plan.style.palette["class_defs"]["process"]["fill"] == "#d9eaf7"
    assert plan.metadata.is_preview_stale is True


def test_style_applier_rejects_unsupported_visual_kind() -> None:
    plan = VisualPlan(visual_kind="diagram", intent="process")
    style = _style()
    style.supported_visual_kinds = ["chart"]

    result = StyleApplier().apply_style(plan, style)

    assert result.success is False
    assert result.errors
