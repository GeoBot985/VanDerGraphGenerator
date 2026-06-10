"""Runtime path resolution tests."""

from __future__ import annotations

import sys

from semantic_visual_builder.runtime.runtime_paths import RuntimePathResolver


def test_runtime_paths_source_mode() -> None:
    paths = RuntimePathResolver().resolve()
    assert paths.app_root == paths.resource_root
    assert paths.asset_dir == paths.app_root / "assets"
    assert paths.export_dir.exists()
    assert paths.log_dir.exists()


def test_runtime_paths_packaged_mode(monkeypatch, tmp_path) -> None:
    exe_path = tmp_path / "VanDerGraphGenerator.exe"
    bundle_root = tmp_path / "bundle"
    bundle_root.mkdir()

    monkeypatch.setattr(sys, "frozen", True, raising=False)
    monkeypatch.setattr(sys, "executable", str(exe_path), raising=False)
    monkeypatch.setattr(sys, "_MEIPASS", str(bundle_root), raising=False)

    paths = RuntimePathResolver().resolve()

    assert paths.is_packaged is True
    assert paths.app_root == exe_path.parent
    assert paths.resource_root == bundle_root
    assert paths.recipes_dir == paths.app_root / "user_data" / "recipes"
    assert paths.config_dir == paths.app_root / "user_data" / "config"
    assert paths.export_dir == paths.app_root / "user_data" / "exports"
    assert paths.log_dir == paths.app_root / "user_data" / "logs"
