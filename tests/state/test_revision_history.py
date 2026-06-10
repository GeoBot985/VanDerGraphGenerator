"""Revision history tests."""

from semantic_visual_builder.planning.visual_plan_schema import VisualPlan
from semantic_visual_builder.state.revision_history import RevisionHistory


def test_add_revision_increments_count() -> None:
    history = RevisionHistory()
    history.add_revision("First", VisualPlan(visual_kind="chart", intent="compare_categories"))
    assert history.count() == 1


def test_latest_returns_last_revision() -> None:
    history = RevisionHistory()
    history.add_revision("First", VisualPlan(visual_kind="chart", intent="compare_categories"))
    latest = history.add_revision("Second", VisualPlan(visual_kind="chart", intent="show_trend"))
    assert history.latest() == latest


def test_revision_numbers_start_at_one() -> None:
    history = RevisionHistory()
    revision = history.add_revision("First", VisualPlan(visual_kind="chart", intent="compare_categories"))
    assert revision.revision_number == 1
