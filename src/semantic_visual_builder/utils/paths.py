"""Path utility helpers."""

from __future__ import annotations

from pathlib import Path


def get_project_root() -> Path:
    """Return the repository root when running from source.

    TODO: add PyInstaller-aware path handling in a later sprint.
    """

    return Path(__file__).resolve().parents[3]


def get_kb_dir() -> Path:
    """Return the product knowledge base directory."""

    return get_project_root() / "kb"


def get_graph_matrix_dir() -> Path:
    """Return the graph matrix directory."""

    return get_project_root() / "graph_matrix"


def get_exports_dir() -> Path:
    """Return the export directory."""

    return get_project_root() / "exports"


def get_assets_dir() -> Path:
    """Return the assets directory."""

    return get_project_root() / "assets"


def get_vendor_assets_dir() -> Path:
    """Return the bundled vendor assets directory."""

    return get_assets_dir() / "vendor"


def get_previews_dir() -> Path:
    """Return the HTML preview directory."""

    return get_exports_dir() / "previews"


def get_recipes_dir() -> Path:
    """Return the recipe directory."""

    return get_project_root() / "recipes"


def get_webview_template_dir() -> Path:
    """Return the HTML template directory."""

    return get_project_root() / "src" / "semantic_visual_builder" / "webview" / "templates"
