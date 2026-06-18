"""Load and prepare gallery sample items into app state."""

from __future__ import annotations

import logging
from pathlib import Path

from .gallery_schema import GalleryItem

_log = logging.getLogger(__name__)


class GalleryRunner:
    """Load a gallery item into the app state.

    The runner sets the prompt, loads the dataset, and optionally loads a recipe.
    It does not auto-call Ollama — the user still triggers generation.
    """

    def run_gallery_item(self, item: GalleryItem, app_state: object) -> list[str]:
        """Prepare app state for the given gallery item. Returns a list of status messages."""
        messages: list[str] = []

        if item.prompt and hasattr(app_state, "conversation_state"):
            try:
                conversation = app_state.conversation_state  # type: ignore[union-attr]
                setter = getattr(conversation, "set_last_user_message", None)
                if callable(setter):
                    setter(item.prompt)
                elif hasattr(conversation, "add_user_message"):
                    conversation.add_user_message(item.prompt)  # type: ignore[union-attr]
                else:
                    raise AttributeError("conversation_state has no prompt setter")
                messages.append(f"Prompt set: {item.prompt}")
            except Exception as exc:
                messages.append(f"Could not set prompt: {exc}")

        if item.sample_dataset_path:
            dataset_path = Path(item.sample_dataset_path)
            if not dataset_path.is_absolute():
                dataset_path = Path.cwd() / dataset_path
            if dataset_path.exists():
                try:
                    self._load_dataset(dataset_path, app_state)
                    messages.append(f"Dataset loaded: {dataset_path.name}")
                except Exception as exc:
                    messages.append(f"Could not load dataset '{dataset_path.name}': {exc}")
            else:
                messages.append(f"Sample dataset not found: {dataset_path}")

        if item.sample_recipe_path:
            recipe_path = Path(item.sample_recipe_path)
            if not recipe_path.is_absolute():
                recipe_path = Path.cwd() / recipe_path
            if recipe_path.exists():
                try:
                    self._load_recipe(recipe_path, app_state)
                    messages.append(f"Recipe loaded: {recipe_path.name}")
                except Exception as exc:
                    messages.append(f"Could not load recipe '{recipe_path.name}': {exc}")
            else:
                messages.append(f"Sample recipe not found: {recipe_path}")

        if hasattr(app_state, "set_active_gallery_item"):
            app_state.set_active_gallery_item(item)  # type: ignore[union-attr]

        return messages

    def _load_dataset(self, path: Path, app_state: object) -> None:
        suffix = path.suffix.lower()
        if suffix == ".csv":
            from semantic_visual_builder.data.csv_loader import CsvLoader
            from semantic_visual_builder.data.data_profiler import DataProfiler
            from semantic_visual_builder.data.dataset_context import (
                DatasetContext,
                DatasetSourceInfo,
            )
            loaded = CsvLoader().load(path)
            profile = DataProfiler().profile(loaded.dataframe)
            ctx = DatasetContext(
                loaded_dataset=loaded,
                profile=profile,
                source_info=DatasetSourceInfo(source_type="sample", path=path),
            )
            app_state.dataset_context = ctx  # type: ignore[attr-defined]
        elif suffix == ".xlsx":
            from semantic_visual_builder.data.csv_loader import LoadedDataset
            from semantic_visual_builder.data.data_profiler import DataProfiler
            from semantic_visual_builder.data.dataset_context import (
                DatasetContext,
                DatasetSourceInfo,
            )
            from semantic_visual_builder.data.excel_loader import ExcelLoader
            info = ExcelLoader().inspect_workbook(path)
            loaded_excel = ExcelLoader().load_sheet(path, info.sheet_names[0])
            loaded = LoadedDataset(path=path, dataframe=loaded_excel.dataframe)
            profile = DataProfiler().profile(loaded.dataframe)
            ctx = DatasetContext(
                loaded_dataset=loaded,
                profile=profile,
                source_info=DatasetSourceInfo(source_type="sample", path=path, sheet_name=loaded_excel.sheet_name),
            )
            app_state.dataset_context = ctx  # type: ignore[attr-defined]

    def _load_recipe(self, path: Path, app_state: object) -> None:
        from semantic_visual_builder.recipes.recipe_store import RecipeStore
        store = RecipeStore(recipes_dir=path.parent)
        recipe = store.load_recipe(path)
        if hasattr(app_state, "set_active_recipe"):
            app_state.set_active_recipe(recipe, path)  # type: ignore[union-attr]
