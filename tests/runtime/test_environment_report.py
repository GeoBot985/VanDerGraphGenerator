"""Environment report tests."""

from __future__ import annotations

from semantic_visual_builder.runtime.environment_report import build_environment_report
from semantic_visual_builder.runtime.runtime_paths import RuntimePaths
from semantic_visual_builder.state.app_state import AppState


def test_environment_report_includes_runtime_paths(tmp_path) -> None:
    runtime_paths = RuntimePaths(
        app_root=tmp_path,
        resource_root=tmp_path / "bundle",
        asset_dir=tmp_path / "bundle" / "assets",
        builtin_styles_dir=tmp_path / "bundle" / "styles" / "builtins",
        user_styles_dir=tmp_path / "user_data" / "styles",
        kb_dir=tmp_path / "bundle" / "kb",
        graph_matrix_dir=tmp_path / "bundle" / "graph_matrix",
        recipes_dir=tmp_path / "user_data" / "recipes",
        config_dir=tmp_path / "user_data" / "config",
        export_dir=tmp_path / "user_data" / "exports",
        log_dir=tmp_path / "user_data" / "logs",
        is_packaged=True,
    )
    app_state = AppState(runtime_paths=runtime_paths)

    report = build_environment_report(runtime_paths, app_state)

    assert "Environment report" in report
    assert "Packaged mode: yes" in report
    assert f"Resource root: {runtime_paths.resource_root}" in report
