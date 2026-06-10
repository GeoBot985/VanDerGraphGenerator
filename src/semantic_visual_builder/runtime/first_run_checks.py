"""First-run environment checks."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from semantic_visual_builder.llm.ollama_client import OllamaClient

from .runtime_paths import RuntimePaths


@dataclass
class FirstRunCheck:
    name: str
    status: str
    message: str
    required: bool = False


@dataclass
class FirstRunReport:
    checks: list[FirstRunCheck] = field(default_factory=list)

    @property
    def has_blocking_issues(self) -> bool:
        return any(check.required and check.status == "error" for check in self.checks)


class FirstRunChecker:
    def __init__(
        self, runtime_paths: RuntimePaths, ollama_client: OllamaClient | None = None
    ):
        self.runtime_paths = runtime_paths
        self.ollama_client = ollama_client or OllamaClient()

    def run(self) -> FirstRunReport:
        checks = [
            self._folder_check(
                "App folders writable",
                self.runtime_paths.export_dir,
                self.runtime_paths.log_dir,
                self.runtime_paths.recipes_dir,
            ),
            self._file_check(
                "KB files present",
                self.runtime_paths.kb_dir / "capabilities.json",
                required=True,
            ),
            self._file_check(
                "Graph matrix present",
                self.runtime_paths.graph_matrix_dir / "graph_matrix.json",
                required=True,
            ),
            self._file_check(
                "Renderer templates present",
                self.runtime_paths.resource_root
                / "src"
                / "semantic_visual_builder"
                / "webview"
                / "templates"
                / "plotly_host.html",
                required=True,
            ),
            self._asset_check(
                "Plotly asset present or CDN fallback available",
                self.runtime_paths.asset_dir / "vendor" / "plotly" / "plotly.min.js",
            ),
            self._asset_check(
                "Mermaid asset present or CDN fallback available",
                self.runtime_paths.asset_dir / "vendor" / "mermaid" / "mermaid.min.js",
            ),
            self._ollama_check(),
            self._sample_check(
                "Sample dataset present",
                self.runtime_paths.asset_dir / "samples" / "sample_transactions.csv",
            ),
            self._sample_check(
                "Sample recipes present",
                self.runtime_paths.resource_root
                / "recipes"
                / "samples"
                / "weekly_transactions.recipe.json",
            ),
        ]
        return FirstRunReport(checks=checks)

    def _folder_check(self, name: str, *paths: Path) -> FirstRunCheck:
        try:
            for path in paths:
                path.mkdir(parents=True, exist_ok=True)
            return FirstRunCheck(name=name, status="ok", message="Writable")
        except Exception as exc:
            return FirstRunCheck(
                name=name, status="error", message=str(exc), required=True
            )

    def _file_check(
        self, name: str, path: Path, required: bool = False
    ) -> FirstRunCheck:
        if path.exists():
            return FirstRunCheck(
                name=name, status="ok", message="Found", required=required
            )
        return FirstRunCheck(
            name=name,
            status="error" if required else "warning",
            message=f"Missing: {path}",
            required=required,
        )

    def _asset_check(self, name: str, path: Path) -> FirstRunCheck:
        if path.exists():
            return FirstRunCheck(name=name, status="ok", message="Local asset present")
        return FirstRunCheck(
            name=name,
            status="warning",
            message="Local asset missing; CDN fallback available",
        )

    def _sample_check(self, name: str, path: Path) -> FirstRunCheck:
        if path.exists():
            return FirstRunCheck(name=name, status="ok", message="Found")
        return FirstRunCheck(name=name, status="warning", message=f"Missing: {path}")

    def _ollama_check(self) -> FirstRunCheck:
        try:
            status = self.ollama_client.get_status()
            if status.is_connected:
                models = self.ollama_client.list_models()
                if models:
                    return FirstRunCheck(
                        name="Ollama reachable",
                        status="ok",
                        message=f"{len(models)} model(s) installed",
                    )
                return FirstRunCheck(
                    name="Ollama reachable",
                    status="warning",
                    message="Ollama reachable, but no models installed",
                )
            return FirstRunCheck(
                name="Ollama reachable", status="warning", message="Ollama not running"
            )
        except Exception as exc:
            return FirstRunCheck(
                name="Ollama reachable", status="warning", message=str(exc)
            )
