"""Logging configuration helpers."""

from __future__ import annotations

import logging


def configure_logging() -> None:
    """Configure simple console logging."""

    if logging.getLogger().handlers:
        return
    logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(name)s:%(message)s")
