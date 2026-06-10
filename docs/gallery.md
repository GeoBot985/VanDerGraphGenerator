# Sample Workflow Gallery

The gallery provides pre-configured examples that load a sample dataset, recipe, and prompt into the app so the user can explore and reproduce typical chart workflows without starting from scratch.

## Gallery Items

Each gallery item is defined in `assets/gallery/gallery_items.json` with the following fields:

| Field | Type | Description |
|-------|------|-------------|
| `item_id` | string | Unique identifier |
| `title` | string | Display name |
| `description` | string | What the example demonstrates |
| `sample_dataset_path` | string or null | Relative path to a sample CSV or XLSX |
| `sample_recipe_path` | string or null | Relative path to a sample recipe JSON |
| `sample_style_id` | string or null | Built-in or user style profile ID to apply |
| `prompt` | string or null | Pre-filled user prompt |
| `expected_visual_kind` | string or null | `"chart"` or `"diagram"` |
| `expected_chart_type` | string or null | e.g. `"bar"`, `"histogram"` |
| `expected_diagram_type` | string or null | e.g. `"flowchart"` |

## Loading a Gallery Item

When the user selects a gallery item, `GalleryRunner.run_gallery_item(item, app_state)`:

1. Loads the sample dataset into `app_state.dataset_context` (if a path is given and the file exists).
2. Loads the sample recipe into `app_state.active_recipe` (if a path is given and the file exists).
3. Sets the prompt in `app_state.conversation_state` (if provided).
4. Calls `app_state.set_active_gallery_item(item)`.

The runner returns a list of status messages describing what was loaded or what failed.

**Important:** The runner does not auto-trigger Ollama generation. The user still presses the generate button.

## Adding Gallery Items

Edit `assets/gallery/gallery_items.json` and add a new object to the `items` array. Place sample data files in `assets/samples/`.

## Limitations

- Gallery items are read-only configuration. Users cannot add, edit, or delete them from within the app.
- If a sample file is missing, the runner reports the path and continues; it does not abort.
- The gallery does not auto-apply styles; `sample_style_id` is reserved for future use.
