"""Recipe schema models."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass
class RecipeMetadata:
    recipe_id: str
    recipe_name: str
    description: str | None = None
    schema_version: str = "2.0"
    app_version_created: str | None = None
    created_at: str | None = None
    updated_at: str | None = None
    author: str | None = None
    tags: list[str] = field(default_factory=list)


@dataclass
class RecipeFieldExpectation:
    role: str
    field_name: str
    semantic_type: str | None = None
    required: bool = True
    aliases: list[str] = field(default_factory=list)
    description: str | None = None


@dataclass
class RecipeStyle:
    title: str | None = None
    subtitle: str | None = None
    colour_scheme: str | None = None
    highlights: dict[str, Any] = field(default_factory=dict)
    labels: dict[str, str] = field(default_factory=dict)
    orientation: str | None = None


@dataclass
class RecipeRenderer:
    renderer: str
    output_type: str | None = None


def _current_utc_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass(init=False)
class VisualRecipe:
    metadata: RecipeMetadata
    expected_fields: list[RecipeFieldExpectation]
    visual_plan_template: dict[str, Any]
    style: RecipeStyle
    renderer: RecipeRenderer | None
    field_mapping_hints: dict[str, list[str]]
    notes: list[str]

    def __init__(
        self,
        metadata: RecipeMetadata | None = None,
        expected_fields: list[RecipeFieldExpectation] | None = None,
        visual_plan_template: dict[str, Any] | None = None,
        style: RecipeStyle | dict[str, Any] | None = None,
        renderer: RecipeRenderer | dict[str, Any] | str | None = None,
        field_mapping_hints: dict[str, list[str]] | None = None,
        notes: list[str] | None = None,
        **legacy: Any,
    ) -> None:
        legacy_recipe_name = legacy.pop("recipe_name", None)
        legacy_schema_version = legacy.pop("schema_version", None)
        legacy_visual_plan = legacy.pop("visual_plan", None)
        legacy_description = legacy.pop("description", None)
        legacy_created_at = legacy.pop("created_at", None)
        legacy_updated_at = legacy.pop("updated_at", None)
        legacy_author = legacy.pop("author", None)
        legacy_tags = legacy.pop("tags", None)
        legacy_app_version_created = legacy.pop("app_version_created", None)

        if metadata is None:
            metadata = RecipeMetadata(
                recipe_id=legacy.pop(
                    "recipe_id", self._default_recipe_id(legacy_recipe_name)
                ),
                recipe_name=legacy_recipe_name
                or legacy.get("recipe_id")
                or "Untitled recipe",
                description=legacy_description,
                schema_version=legacy_schema_version or "2.0",
                app_version_created=legacy_app_version_created,
                created_at=legacy_created_at or _current_utc_iso(),
                updated_at=legacy_updated_at,
                author=legacy_author,
                tags=list(legacy_tags or []),
            )
        else:
            metadata = RecipeMetadata(**asdict(metadata))

        if isinstance(style, dict):
            style = RecipeStyle(
                title=style.get("title"),
                subtitle=style.get("subtitle"),
                colour_scheme=style.get("colour_scheme"),
                highlights=dict(style.get("highlights", {}) or {}),
                labels=dict(style.get("labels", {}) or {}),
                orientation=style.get("orientation"),
            )
        elif style is None:
            style = RecipeStyle()

        if isinstance(renderer, str):
            renderer = RecipeRenderer(renderer=renderer)
        elif isinstance(renderer, dict):
            renderer = RecipeRenderer(
                renderer=str(renderer.get("renderer", "")),
                output_type=renderer.get("output_type")
                or renderer.get("output_format"),
            )

        self.metadata = metadata
        self.expected_fields = list(expected_fields or [])
        self.visual_plan_template = dict(
            visual_plan_template or legacy_visual_plan or {}
        )
        self.style = style
        self.renderer = renderer
        self.field_mapping_hints = dict(field_mapping_hints or {})
        self.notes = list(notes or [])

    @staticmethod
    def _default_recipe_id(recipe_name: str | None) -> str:
        if not recipe_name:
            return "untitled_recipe"
        import re

        text = re.sub(r"[^A-Za-z0-9]+", "_", recipe_name.strip().lower())
        return text.strip("_") or "untitled_recipe"

    @property
    def recipe_name(self) -> str:
        return self.metadata.recipe_name

    @recipe_name.setter
    def recipe_name(self, value: str) -> None:
        self.metadata.recipe_name = value

    @property
    def schema_version(self) -> str:
        return self.metadata.schema_version

    @schema_version.setter
    def schema_version(self, value: str) -> None:
        self.metadata.schema_version = value

    @property
    def visual_plan(self) -> dict[str, Any]:
        return self.visual_plan_template

    @visual_plan.setter
    def visual_plan(self, value: dict[str, Any]) -> None:
        self.visual_plan_template = value

    @property
    def description(self) -> str | None:
        return self.metadata.description

    @description.setter
    def description(self, value: str | None) -> None:
        self.metadata.description = value

    @property
    def created_at(self) -> str | None:
        return self.metadata.created_at

    @created_at.setter
    def created_at(self, value: str | None) -> None:
        self.metadata.created_at = value

    @property
    def updated_at(self) -> str | None:
        return self.metadata.updated_at

    @updated_at.setter
    def updated_at(self, value: str | None) -> None:
        self.metadata.updated_at = value

    def to_dict(self) -> dict[str, Any]:
        return {
            "metadata": asdict(self.metadata),
            "expected_fields": [asdict(item) for item in self.expected_fields],
            "visual_plan_template": self.visual_plan_template,
            "style": asdict(self.style),
            "renderer": asdict(self.renderer) if self.renderer is not None else None,
            "field_mapping_hints": self.field_mapping_hints,
            "notes": list(self.notes),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "VisualRecipe":
        metadata_data = data.get("metadata") or {}
        metadata = RecipeMetadata(
            recipe_id=str(metadata_data.get("recipe_id", data.get("recipe_id", ""))),
            recipe_name=str(
                metadata_data.get(
                    "recipe_name", data.get("recipe_name", "Untitled recipe")
                )
            ),
            description=metadata_data.get("description", data.get("description")),
            schema_version=str(
                metadata_data.get("schema_version", data.get("schema_version", "2.0"))
            ),
            app_version_created=metadata_data.get(
                "app_version_created", data.get("app_version_created")
            ),
            created_at=metadata_data.get("created_at", data.get("created_at")),
            updated_at=metadata_data.get("updated_at", data.get("updated_at")),
            author=metadata_data.get("author", data.get("author")),
            tags=list(metadata_data.get("tags", data.get("tags", [])) or []),
        )
        expected_fields = [
            RecipeFieldExpectation(
                role=str(item.get("role", "")),
                field_name=str(item.get("field_name", "")),
                semantic_type=item.get("semantic_type"),
                required=bool(item.get("required", True)),
                aliases=list(item.get("aliases", []) or []),
                description=item.get("description"),
            )
            for item in data.get("expected_fields", [])
            if isinstance(item, dict)
        ]
        style_data = data.get("style", {}) or {}
        style = RecipeStyle(
            title=style_data.get("title"),
            subtitle=style_data.get("subtitle"),
            colour_scheme=style_data.get("colour_scheme"),
            highlights=dict(style_data.get("highlights", {}) or {}),
            labels=dict(style_data.get("labels", {}) or {}),
            orientation=style_data.get("orientation"),
        )
        renderer_data = data.get("renderer")
        renderer = None
        if isinstance(renderer_data, dict) and renderer_data.get("renderer"):
            renderer = RecipeRenderer(
                renderer=str(renderer_data.get("renderer")),
                output_type=renderer_data.get("output_type")
                or renderer_data.get("output_format"),
            )
        elif isinstance(renderer_data, str) and renderer_data:
            renderer = RecipeRenderer(renderer=renderer_data)
        return cls(
            metadata=metadata,
            expected_fields=expected_fields,
            visual_plan_template=dict(
                data.get("visual_plan_template") or data.get("visual_plan") or {}
            ),
            style=style,
            renderer=renderer,
            field_mapping_hints={
                key: list(value)
                for key, value in (data.get("field_mapping_hints", {}) or {}).items()
                if isinstance(value, list)
            },
            notes=list(data.get("notes", []) or []),
        )
