"""Application bootstrap."""

from __future__ import annotations

import argparse

from semantic_visual_builder.knowledge.graph_matrix import GraphMatrixLoader
from semantic_visual_builder.knowledge.product_kb import ProductKnowledgeLoader
from semantic_visual_builder.runtime.environment_report import build_environment_report
from semantic_visual_builder.runtime.first_run_checks import FirstRunChecker
from semantic_visual_builder.runtime.runtime_paths import (
    RuntimePathResolver,
    RuntimePaths,
)
from semantic_visual_builder.state.app_state import AppState
from semantic_visual_builder.ui.tkinter_app import SemanticVisualBuilderApp
from semantic_visual_builder.utils.error_handling import (
    format_exception_for_log,
    user_friendly_error,
)
from semantic_visual_builder.utils.logging_config import configure_logging, get_logger
from semantic_visual_builder.utils.paths import get_runtime_paths
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
    return state


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog="semantic_visual_builder", add_help=True)
    parser.add_argument("--smoke-test", action="store_true")
    parser.add_argument("--version", action="store_true")
    parser.add_argument("--env-report", action="store_true")
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
