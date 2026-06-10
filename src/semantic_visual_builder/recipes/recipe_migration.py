"""Recipe migration placeholder."""

from __future__ import annotations


class RecipeMigration:
    def migrate_to_current(self, raw: dict) -> dict:
        schema_version = str(
            raw.get("metadata", {}).get("schema_version")
            or raw.get("schema_version")
            or ""
        )
        if schema_version == "2.0":
            return raw
        raise NotImplementedError(
            "Recipe migration is only implemented for schema_version 2.0 in Sprint 8."
        )
