"""Architecture guards for legacy deterministic input routing."""

from pathlib import Path


def test_tkinter_app_does_not_import_message_classifier() -> None:
    source = Path("src/semantic_visual_builder/ui/tkinter_app.py").read_text()
    assert "MessageClassifier" not in source


def test_tkinter_app_does_not_import_message_intent() -> None:
    source = Path("src/semantic_visual_builder/ui/tkinter_app.py").read_text()
    assert "MessageIntent" not in source


def test_send_chat_delegates_to_semantic_input_orchestrator() -> None:
    source = Path("src/semantic_visual_builder/ui/tkinter_app.py").read_text()
    assert "semantic_input_orchestrator.handle_message(" in source


def test_refinement_engine_does_not_parse_raw_user_text() -> None:
    source = Path(
        "src/semantic_visual_builder/planning/refinement_engine.py"
    ).read_text()
    assert "lower()" not in source
    assert "make it a bar chart" not in source
    assert "highlight" not in source.lower()


def test_visual_plan_patch_applier_accepts_structured_patch_only() -> None:
    source = Path(
        "src/semantic_visual_builder/planning/visual_plan_patch_applier.py"
    ).read_text()
    assert "VisualPlanPatch" in source
    assert "message.lower" not in source
    assert "user_message" not in source
