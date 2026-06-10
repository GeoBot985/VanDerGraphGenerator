"""Preview panel tests."""

from semantic_visual_builder.planning.visual_plan_schema import VisualPlan
from semantic_visual_builder.state.app_state import AppState
from semantic_visual_builder.ui.preview_panel import PreviewPanel


def test_preview_status_text_can_be_derived_from_app_state() -> None:
    state = AppState()
    panel = PreviewPanel()
    assert panel.preview_status_text(state) == "No visual plan yet."
    state.current_visual_plan = VisualPlan(visual_kind="chart", intent="compare_categories", chart_type="bar")
    assert panel.preview_status_text(state) == "Preview stale. Regenerate to reflect latest plan."
