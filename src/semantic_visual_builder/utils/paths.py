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
