"""Packaging manifest tests."""

from __future__ import annotations

from pathlib import Path


def test_pyinstaller_spec_exists_and_references_key_resources() -> None:
    spec = (
        Path(__file__).resolve().parents[2]
        / "build"
        / "pyinstaller"
        / "VanDerGraphGenerator.spec"
    )
    text = spec.read_text(encoding="utf-8")

    assert "VanDerGraphGenerator" in text
    assert "assets" in text
    assert "graph_matrix" in text
    assert "recipes/samples" in text
    assert "Analysis(" in text
    assert "COLLECT(" in text
