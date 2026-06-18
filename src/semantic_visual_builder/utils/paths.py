"""Path utility helpers."""

from __future__ import annotations

from pathlib import Path

from semantic_visual_builder.runtime.runtime_paths import (
    RuntimePathResolver,
    RuntimePaths,
)

_DEFAULT_RUNTIME_PATHS: RuntimePaths | None = None


def get_runtime_paths() -> RuntimePaths:
    global _DEFAULT_RUNTIME_PATHS
    if _DEFAULT_RUNTIME_PATHS is None:
        _DEFAULT_RUNTIME_PATHS = RuntimePathResolver().resolve()
    return _DEFAULT_RUNTIME_PATHS


def get_project_root() -> Path:
    """Return the repository root when running from source.

    TODO: add PyInstaller-aware path handling in a later sprint.
    """

    return Path(__file__).resolve().parents[3]


def get_kb_dir() -> Path:
    """Return the product knowledge base directory."""

    return get_runtime_paths().kb_dir


def get_graph_matrix_dir() -> Path:
    """Return the graph matrix directory."""

    return get_runtime_paths().graph_matrix_dir


def get_exports_dir() -> Path:
    """Return the export directory."""

    return get_runtime_paths().export_dir


def get_assets_dir() -> Path:
    """Return the assets directory."""

    return get_runtime_paths().asset_dir


def get_builtin_styles_dir() -> Path:
    """Return the bundled built-in styles directory."""

    return get_runtime_paths().builtin_styles_dir


def get_user_styles_dir() -> Path:
    """Return the writable user styles directory."""

    return get_runtime_paths().user_styles_dir


def get_vendor_assets_dir() -> Path:
    """Return the bundled vendor assets directory."""

    return get_assets_dir() / "vendor"


def get_previews_dir() -> Path:
    """Return the HTML preview directory."""

    return get_exports_dir() / "previews"


def get_recipes_dir() -> Path:
    """Return the recipe directory."""

    return get_runtime_paths().recipes_dir


def get_webview_template_dir() -> Path:
    """Return the HTML template directory."""

    runtime_paths = get_runtime_paths()
    return (
        runtime_paths.resource_root
        / "src"
        / "semantic_visual_builder"
        / "webview"
        / "templates"
    )

def get_gallery_dir() -> Path:
    """Return the bundled gallery config directory."""

    return get_assets_dir() / "gallery"


def get_gallery_path() -> Path:
    """Return the gallery items JSON config path."""

    return get_gallery_dir() / "gallery_items.json"


def get_settings_path() -> Path:
    """Return the user app settings JSON path."""

    return get_runtime_paths().config_dir / "app_settings.json"
