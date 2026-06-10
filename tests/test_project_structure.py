"""Project structure tests."""

from pathlib import Path


def test_key_folders_exist() -> None:
    root = Path(__file__).resolve().parents[1]
    for rel in [
        "docs",
        "config",
        "assets",
        "kb",
        "graph_matrix",
        "src/semantic_visual_builder",
        "tests",
        "scripts",
        "build/pyinstaller",
    ]:
        assert (root / rel).exists()
