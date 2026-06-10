"""User-friendly error helpers."""

from __future__ import annotations


def user_friendly_error(exc: Exception) -> str:
    text = str(exc).lower()
    if "csv" in text or "delimiter" in text:
        return "The selected CSV could not be loaded. Check the file format."
    if "kb" in text or "knowledge" in text:
        return "Required knowledge-base files are missing."
    if "ollama" in text or "connection" in text:
        return "Ollama is not reachable. Start Ollama or use deterministic mapping."
    if "recipe" in text:
        return "This recipe does not match the current dataset."
    if "preview" in text or "render" in text:
        return "Preview could not be generated. See debug details."
    return "Something went wrong. See the logs for details."


def format_exception_for_log(exc: Exception) -> str:
    return f"{type(exc).__name__}: {exc}"
