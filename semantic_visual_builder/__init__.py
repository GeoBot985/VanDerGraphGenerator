"""Bootstrap package so `python -m semantic_visual_builder` works from the repo root."""

from __future__ import annotations

from pkgutil import extend_path
from pathlib import Path

__path__ = extend_path(__path__, __name__)
_src_package = Path(__file__).resolve().parent.parent / "src" / "semantic_visual_builder"
if _src_package.exists():
    __path__.append(str(_src_package))

