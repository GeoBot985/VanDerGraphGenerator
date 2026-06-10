"""Style extraction action tests."""

from pathlib import Path

from PIL import Image, ImageDraw

from semantic_visual_builder.planning.visual_plan_schema import VisualPlan
from semantic_visual_builder.state.app_state import AppState
from semantic_visual_builder.styles.style_manager import StyleManager
from semantic_visual_builder.styles.style_store import StyleStore
from semantic_visual_builder.styles.style_validator import StyleValidator
from semantic_visual_builder.ui.tkinter_app import SemanticVisualBuilderApp


class FakeVar:
    def __init__(self, value: str = "") -> None:
        self.value = value

    def get(self) -> str:
        return self.value

    def set(self, value: str) -> None:
        self.value = value


def _make_image(path: Path) -> None:
    image = Image.new("RGB", (400, 240), "#ffffff")
    draw = ImageDraw.Draw(image)
    draw.rectangle([50, 40, 180, 200], fill="#1f4e79")
    draw.rectangle([220, 80, 350, 200], fill="#70ad47")
    image.save(path)


def test_extract_save_and_apply_extracted_style(monkeypatch, tmp_path: Path) -> None:
    image_path = tmp_path / "sample.png"
    _make_image(image_path)

    state = AppState()
    state.current_visual_plan = VisualPlan(visual_kind="chart", intent="compare")
    app = SemanticVisualBuilderApp(state, build_ui=False)
    app.style_store = StyleStore(tmp_path / "user", tmp_path / "builtin")
    app.style_validator = StyleValidator()
    app.style_manager = StyleManager(app.style_store, app.style_validator)
    app._style_image_var = FakeVar(str(image_path))
    app._style_image_model_var = FakeVar("")
    app._use_vision_var = FakeVar(False)
    app._refresh_all_views = lambda: None
    app._refresh_available_styles = lambda: None

    extract_message = app.extract_style_action()

    assert "Extracted style draft" in extract_message
    assert state.last_style_extraction_result is not None

    monkeypatch.setattr(
        "semantic_visual_builder.ui.tkinter_app.simpledialog.askstring",
        lambda *args, **kwargs: "Extracted Blue Report Style",
    )

    save_message = app.save_extracted_style_action()

    assert "Extracted style saved:" in save_message

    apply_message = app.apply_extracted_style_action()

    assert "Applied extracted style:" in apply_message
    assert state.current_visual_plan is not None
    assert state.current_visual_plan.metadata.is_preview_stale is True
