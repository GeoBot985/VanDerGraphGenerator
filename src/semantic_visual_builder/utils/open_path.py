"""Cross-platform helpers for opening files and folders in the OS file manager."""

from __future__ import annotations

import platform
import subprocess
from pathlib import Path


def open_in_os(path: Path | str) -> str:
    """Open a file or folder using the platform-native handler.

    Returns a short status string. Uses os.startfile on Windows, ``open`` on
    macOS, and ``xdg-open`` on Linux/other. Falls back to a clear message when
    no handler is available.
    """
    target = str(path)
    system = platform.system()
    try:
        if system == "Windows":
            import os

            os.startfile(target)  # type: ignore[attr-defined]
        elif system == "Darwin":
            subprocess.run(["open", target], check=False)
        else:
            subprocess.run(["xdg-open", target], check=False)
        return f"Opened: {target}"
    except Exception as exc:
        return f"Could not open {target}: {exc}"
