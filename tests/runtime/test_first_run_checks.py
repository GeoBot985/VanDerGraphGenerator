"""First-run checker tests."""

from __future__ import annotations

from semantic_visual_builder.runtime.first_run_checks import FirstRunChecker
from semantic_visual_builder.runtime.runtime_paths import RuntimePaths


class FakeOllamaClient:
    def get_status(self):
        class Status:
            is_connected = False
            version = None
            error = None

        return Status()

    def list_models(self):
        return []


def test_first_run_checker_reports_required_files(tmp_path) -> None:
    resource_root = tmp_path / "bundle"
    asset_dir = resource_root / "assets"
    kb_dir = resource_root / "kb"
    graph_matrix_dir = resource_root / "graph_matrix"
    recipes_dir = tmp_path / "user_data" / "recipes"
    config_dir = tmp_path / "user_data" / "config"
    export_dir = tmp_path / "user_data" / "exports"
    log_dir = tmp_path / "user_data" / "logs"

    (resource_root / "src" / "semantic_visual_builder" / "webview" / "templates").mkdir(
        parents=True
    )
    (asset_dir / "vendor" / "plotly").mkdir(parents=True)
    (asset_dir / "vendor" / "mermaid").mkdir(parents=True)
    (asset_dir / "samples").mkdir(parents=True)
    kb_dir.mkdir(parents=True)
    graph_matrix_dir.mkdir(parents=True)
    recipes_dir.mkdir(parents=True)
    config_dir.mkdir(parents=True)
    export_dir.mkdir(parents=True)
    log_dir.mkdir(parents=True)

    (kb_dir / "capabilities.json").write_text("{}", encoding="utf-8")
    (graph_matrix_dir / "graph_matrix.json").write_text("{}", encoding="utf-8")
    (
        resource_root
        / "src"
        / "semantic_visual_builder"
        / "webview"
        / "templates"
        / "plotly_host.html"
    ).write_text("<html></html>", encoding="utf-8")
    (asset_dir / "vendor" / "plotly" / "plotly.min.js").write_text(
        "/* plotly */", encoding="utf-8"
    )
    (asset_dir / "vendor" / "mermaid" / "mermaid.min.js").write_text(
        "/* mermaid */", encoding="utf-8"
    )
    (asset_dir / "samples" / "sample_transactions.csv").write_text(
        "a,b\n1,2\n", encoding="utf-8"
    )
    (resource_root / "recipes" / "samples").mkdir(parents=True)
    (
        resource_root / "recipes" / "samples" / "weekly_transactions.recipe.json"
    ).write_text("{}", encoding="utf-8")

    runtime_paths = RuntimePaths(
        app_root=tmp_path,
        resource_root=resource_root,
        asset_dir=asset_dir,
        kb_dir=kb_dir,
        graph_matrix_dir=graph_matrix_dir,
        recipes_dir=recipes_dir,
        config_dir=config_dir,
        export_dir=export_dir,
        log_dir=log_dir,
        is_packaged=True,
    )

    report = FirstRunChecker(runtime_paths, ollama_client=FakeOllamaClient()).run()

    assert report.has_blocking_issues is False
    assert any(
        check.name == "KB files present" and check.status == "ok"
        for check in report.checks
    )
