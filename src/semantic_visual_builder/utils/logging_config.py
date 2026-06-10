"""Logging configuration helpers."""

from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler

from semantic_visual_builder.version import APP_VERSION

from .paths import RuntimePaths, get_runtime_paths


def configure_logging(
    runtime_paths: RuntimePaths | None = None, debug: bool = False
) -> None:
    """Configure console and file logging."""

    runtime_paths = runtime_paths or get_runtime_paths()
    root = logging.getLogger()
    if root.handlers:
        return
    root.setLevel(logging.DEBUG if debug else logging.INFO)
    formatter = logging.Formatter(
        f"%(asctime)s %(levelname)s [{APP_VERSION}] %(name)s: %(message)s"
    )
    console = logging.StreamHandler()
    console.setFormatter(formatter)
    root.addHandler(console)
    runtime_paths.log_dir.mkdir(parents=True, exist_ok=True)
    file_handler = RotatingFileHandler(
        runtime_paths.log_dir / "app.log",
        maxBytes=1_000_000,
        backupCount=1,
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)
    root.addHandler(file_handler)


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
