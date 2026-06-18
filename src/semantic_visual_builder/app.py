"""Application bootstrap."""

from __future__ import annotations

import argparse
from pathlib import Path

from semantic_visual_builder.knowledge.graph_matrix import GraphMatrixLoader
from semantic_visual_builder.knowledge.product_kb import ProductKnowledgeLoader
from semantic_visual_builder.runtime.environment_report import build_environment_report
from semantic_visual_builder.runtime.first_run_checks import FirstRunChecker
from semantic_visual_builder.runtime.runtime_paths import (
    RuntimePathResolver,
    RuntimePaths,
)
from semantic_visual_builder.settings.settings_manager import SettingsManager
from semantic_visual_builder.settings.settings_store import SettingsStore
from semantic_visual_builder.state.app_state import AppState
from semantic_visual_builder.ui.tkinter_app import SemanticVisualBuilderApp
from semantic_visual_builder.utils.error_handling import (
    format_exception_for_log,
    user_friendly_error,
)
from semantic_visual_builder.utils.logging_config import configure_logging, get_logger
from semantic_visual_builder.utils.paths import get_runtime_paths, get_settings_path
from semantic_visual_builder.version import APP_NAME, APP_VERSION


def create_app_state(runtime_paths: RuntimePaths | None = None) -> AppState:
    runtime_paths = runtime_paths or get_runtime_paths()
    state = AppState(runtime_paths=runtime_paths)
    try:
        state.product_kb = ProductKnowledgeLoader(runtime_paths.kb_dir).load()
    except Exception as exc:
        state.add_status(f"Product KB load failed: {exc}")
    try:
        state.graph_matrix = GraphMatrixLoader(
            runtime_paths.graph_matrix_dir / "graph_matrix.json"
        ).load()
    except Exception as exc:
        state.add_status(f"Graph matrix load failed: {exc}")
    try:
        manager = SettingsManager(SettingsStore(get_settings_path()))
        settings = manager.load_settings()
        manager.apply_to_app_state(settings, state)
        state.add_status("Settings loaded.")
    except Exception as exc:
        state.add_status(f"Settings load failed: {exc}")
    return state



def _load_startup_dataset(state: AppState, path: Path) -> None:
    """Load a CSV or Excel dataset into app state before the UI starts."""
    try:
        suffix = path.suffix.lower()
        if suffix == ".csv":
            from semantic_visual_builder.data.csv_loader import CsvLoader
            from semantic_visual_builder.data.data_profiler import DataProfiler

            loaded = CsvLoader().load(path)
            profile = DataProfiler().profile(loaded.dataframe)
        elif suffix == ".xlsx":
            from semantic_visual_builder.data.csv_loader import LoadedDataset
            from semantic_visual_builder.data.data_profiler import DataProfiler
            from semantic_visual_builder.data.excel_loader import ExcelLoader

            info = ExcelLoader().inspect_workbook(path)
            loaded_excel = ExcelLoader().load_sheet(path, info.sheet_names[0])
            loaded = LoadedDataset(path=path, dataframe=loaded_excel.dataframe)
            profile = DataProfiler().profile(loaded.dataframe)
        else:
            state.add_status(f"Unsupported startup dataset type: {suffix}")
            return
        state.dataset_context.loaded_dataset = loaded
        state.dataset_context.profile = profile
        state.add_status(f"Loaded startup dataset: {path.name}")
    except Exception as exc:
        state.add_status(f"Startup dataset load failed: {exc}")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog="semantic_visual_builder", add_help=True)
    parser.add_argument("--smoke-test", action="store_true")
    parser.add_argument("--version", action="store_true")
    parser.add_argument("--env-report", action="store_true")
    parser.add_argument(
        "--no-llm",
        action="store_true",
        help="Disable LLM semantic mapping for this run (use deterministic fallback).",
    )
    parser.add_argument(
        "--dataset",
        type=str,
        default=None,
        help="Load a CSV/Excel dataset at startup for headless demos.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        runtime_paths = RuntimePathResolver().resolve()
        configure_logging(runtime_paths)
        logger = get_logger(__name__)
        logger.info("%s %s starting", APP_NAME, APP_VERSION)

        if args.version:
            print(f"{APP_NAME} {APP_VERSION}")
            return 0

        state = create_app_state(runtime_paths)
        if args.no_llm:
            state.llm_mapping_enabled = False
            state.set_app_settings(state.app_settings)
        if args.dataset:
            _load_startup_dataset(state, Path(args.dataset))
        report = FirstRunChecker(runtime_paths).run()
        state.add_status("First-run checks complete.")
        for check in report.checks:
            state.add_status(f"{check.name}: {check.status} - {check.message}")
        logger.info("Startup checks complete; blocking=%s", report.has_blocking_issues)

        if args.smoke_test:
            print(build_environment_report(runtime_paths, state))
            return 1 if report.has_blocking_issues else 0

        if args.env_report:
            print(build_environment_report(runtime_paths, state))
            return 0

        app = SemanticVisualBuilderApp(state)
        try:
            app.run()
            return 0
        except Exception as exc:
            logger.exception(
                "Unhandled application error: %s", format_exception_for_log(exc)
            )
            print(user_friendly_error(exc))
            return 1
    except Exception as exc:
        logger = get_logger(__name__)
        logger.exception("Startup failure: %s", format_exception_for_log(exc))
        print(user_friendly_error(exc))
        return 1
