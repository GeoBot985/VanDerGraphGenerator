"""Regenerate styles/builtins/*.style.json from the Python definitions.

The running app surfaces built-in styles by globbing ``styles/builtins/*.style.json``
(see ``StyleStore.list_builtin_styles``). ``built_in_styles.list_builtin_style_profiles``
is the single source of truth; run this script after changing it to keep the
on-disk JSON in sync.

Usage:
    python scripts/generate_builtin_styles.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from semantic_visual_builder.styles.built_in_styles import (  # noqa: E402
    list_builtin_style_profiles,
)
from semantic_visual_builder.styles.style_validator import (  # noqa: E402
    StyleValidator,
)


def main() -> int:
    target_dir = Path(__file__).resolve().parents[1] / "styles" / "builtins"
    target_dir.mkdir(parents=True, exist_ok=True)

    validator = StyleValidator()
    profiles = list_builtin_style_profiles()
    written = 0
    for profile in profiles:
        result = validator.validate_style(profile)
        if not result.is_valid:
            messages = [message.message for message in result.messages]
            print(f"INVALID {profile.style_id}: {messages}")
            return 1
        data = profile.to_dict()
        # created_at/updated_at are regenerated each run; keep files stable.
        data["metadata"].pop("created_at", None)
        data["metadata"].pop("updated_at", None)
        path = target_dir / f"{profile.style_id}.style.json"
        path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        written += 1

    print(f"Wrote {written} built-in style files to {target_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
