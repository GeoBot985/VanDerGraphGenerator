"""Text sanitization helpers."""

from __future__ import annotations

import re


def sanitize_label(text: str) -> str:
    cleaned = text.replace("\r", " ").replace("\n", " ")
    cleaned = cleaned.replace('"', "'")
    cleaned = re.sub(r"[`{}<>]", "", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned)
    return cleaned.strip()


def normalize_name(text: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9]+", "_", text.strip().lower())
    return cleaned.strip("_")
