"""Resolve runtime paths for source and packaged modes."""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class RuntimePaths:
    app_root: Path
    resource_root: Path
    asset_dir: Path
    builtin_styles_dir: Path
    user_styles_dir: Path
    kb_dir: Path
    graph_matrix_dir: Path
    recipes_dir: Path
    config_dir: Path
    export_dir: Path
    log_dir: Path
    is_packaged: bool


class RuntimePathResolver:
    """Resolve folders relative to source or packaged runtime roots."""

    def __init__(self, app_name: str = "VanDerGraphGenerator"):
        self.app_name = app_name

    def resolve(self) -> RuntimePaths:
        is_packaged = bool(getattr(sys, "frozen", False))
        if is_packaged:
            exe_path = Path(sys.executable).resolve()
            app_root = exe_path.parent
            internal_root = Path(getattr(sys, "_MEIPASS", app_root)).resolve()
            resource_root = internal_root
            asset_dir = internal_root / "assets"
            builtin_styles_dir = internal_root / "styles" / "builtins"
            user_styles_dir = app_root / "user_data" / "styles"
            kb_dir = internal_root / "kb"
            graph_matrix_dir = internal_root / "graph_matrix"
            recipes_dir = app_root / "user_data" / "recipes"
            config_dir = app_root / "user_data" / "config"
            export_dir = app_root / "user_data" / "exports"
            log_dir = app_root / "user_data" / "logs"
        else:
            source_root = Path(__file__).resolve().parents[3]
            app_root = source_root
            resource_root = source_root
            asset_dir = source_root / "assets"
            builtin_styles_dir = source_root / "styles" / "builtins"
            user_styles_dir = source_root / "user_data" / "styles"
            kb_dir = source_root / "kb"
            graph_matrix_dir = source_root / "graph_matrix"
            recipes_dir = source_root / "recipes"
            config_dir = source_root / "config"
            export_dir = source_root / "exports"
            log_dir = source_root / "logs"

        for path in (builtin_styles_dir, user_styles_dir, recipes_dir, config_dir, export_dir, log_dir):
            path.mkdir(parents=True, exist_ok=True)

        return RuntimePaths(
            app_root=app_root,
            resource_root=resource_root,
            asset_dir=asset_dir,
            builtin_styles_dir=builtin_styles_dir,
            user_styles_dir=user_styles_dir,
            kb_dir=kb_dir,
            graph_matrix_dir=graph_matrix_dir,
            recipes_dir=recipes_dir,
            config_dir=config_dir,
            export_dir=export_dir,
            log_dir=log_dir,
            is_packaged=is_packaged,
        )
