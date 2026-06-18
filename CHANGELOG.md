# Changelog

## Unreleased (composite built-in styles)

### Built-in styles are now full design systems, not just colour schemes
The previous built-in colour-scheme styles (corporate_blue, minimal_grey,
dark_slate, ocean, etc.) have been removed and replaced with 14 composite
styles. Each style combines a colour palette **with a typographic identity**
(font family, weight, title/label/tick sizes) **and a chart surface
treatment** (background, plot background, grid, legend position, label
density, title alignment, bar gap, line shape), so switching a style changes
the whole feel of a chart or diagram, not just its data colours.

The new set: Editorial Serif, Magazine Bold, Boardroom, Minimal Swiss,
Technical Report, Academic Paper, Dashboard Dark, Terminal Neon, Pastel Soft,
Marketing Punch, Ocean Cool, Sunset Warm, Colorblind Safe, High Contrast Print.

- Distinct typographic identities span serif (Georgia, Times New Roman), sans
  (Helvetica, Segoe UI, Verdana, Arial) and monospace (Courier New), with
  weights and sizes that vary per style (title sizes from 16 to 28).
- Surface treatments vary too: dark dashboards, cream editorial backgrounds,
  no-grid minimal layouts, medium-grid print styles, bottom/right/none
  legends, and spline vs linear line shapes.
- `styles/builtins/*.style.json` regenerated via
  `scripts/generate_builtin_styles.py`; the previous built-in JSON files were
  removed.
- Stale leftover user-extracted test styles (dark_and_neon, grrr, etc.) cleared
  from `user_data/styles` so the catalog is just the 14 composites.
- `style_panel` and `style_comparison_panel` no longer hardcode the old
  built-in IDs; the built-in set is derived from `list_builtin_style_profiles`,
  so new built-ins are correctly labelled and protected from replacement.
- New tests assert each style is a full composite (typography + surface +
  palette) and that the set has distinct typographic identities. All 14 styles
  render both Plotly charts and Mermaid diagrams.

### Bug fix
- Plotly style adapter no longer crashes with `'str' object has no attribute
  'setdefault'` when a style with a label size is applied to a chart whose axis
  titles are plain strings. String axis titles are now coerced to
  `{"text": ...}` before the font size is attached.

### Internal
- 563 tests; all passing.


## Unreleased (settings plumbing, real dialog, polish)

### Settings now flow into the runtime
- `AppSettings` gained `ollama_base_url` and `generation_timeout_seconds`.
  `OllamaClient` is now built from settings (`_build_ollama_client`) in both
  the constructor and `refresh_ollama`, so a non-default Ollama host/port is
  configurable instead of hardcoded.
- `default_export_dir` is honored by export requests; `prefer_local_renderer_assets`
  drives the `AssetManager`; `open_preview_after_generation` gates the
  auto-open preview step in `generate_preview`.
- `config/app_settings.example.json` now mirrors the actual persisted schema.

### Real Settings dialog
- Replaced the sequential `simpledialog` prompts with a proper `tk.Toplevel`
  form covering the whole `AppSettings` surface: Ollama URL, model, generation
  timeout, renderer (plotly/mermaid), export dir, LLM mapping, prefer-local
  assets, open-preview-after-generation, and debug mode. Save validates via
  `SettingsDialogController`, rebuilds the Ollama client + renderer host, and
  refreshes the model list.

### Chart.js surface trimmed
- The Settings renderer dropdown and `SettingsDialogController` validation now
  only offer `plotly` and `mermaid`; `chartjs` is rejected with a clear
  message so users never pick a renderer that can't render. The renderer module
  and the routing-time rejection guard remain in place.

### Cross-platform open
- New `utils/open_path.py` (`open_in_os`) replaces all `os.startfile` calls, so
  opening previews / logs / exports no longer crashes on macOS and Linux.
  `os` is no longer imported by the Tkinter app.

### Style review wired into extraction
- After image style extraction, an `EditableStyleDraft` is built and stored.
  A new `Style -> Review Extracted Style...` action opens a `StyleReviewDialog`
  Toplevel where the user edits palette colours, grid, label density, tone, and
  tags, then chooses Save (persist + set active), Apply (apply to current plan),
  or Cancel. Extraction no longer jumps straight to applying/saving the raw
  draft.

### Headless / demo flags
- `--no-llm` disables LLM semantic mapping for the run (deterministic fallback).
- `--dataset PATH` loads a CSV or Excel dataset at startup for headless demos
  and screenshots.

### Gallery UX
- `Gallery -> Run Gallery Item by ID...` now opens a combobox of loaded item
  titles instead of asking for a free-text ID.

### Lint + CI
- `ruff` baseline cleaned up (47 import-sort/unused-import errors auto-fixed)
  and `E501` ignored in `pyproject.toml` so `ruff check src tests` is green.
- New `.github/workflows/ci.yml` runs `ruff check` plus `pytest` on Ubuntu and
  Windows, installing Playwright + Chromium so the browser export tests run.

### Internal
- Stale TODO removed from `utils/paths.get_project_root` (PyInstaller-aware
  resolution lives in `runtime_paths`).
- New `tests/utils/test_open_path.py` and architecture guards for the new
  settings fields, dialog validation, `open_in_os`, style review wiring, and
  headless flags.
- 554 tests; all passing (was 545).


## Unreleased (follow-up: real export + conversational refinement)

### Multi-format export is now real
- **PNG export** ? `PngExporter` now renders the generated chart HTML in
  headless Chromium via Playwright and screenshots the `#chart` element to a
  real PNG file. `File -> Export PNG...` produces an actual image.
- **SVG export** ? `SvgExporter` extracts the rendered `<svg>` node (Plotly
  chart or Mermaid diagram) from the headless render and writes a standalone
  `.svg` file. `File -> Export SVG...` produces an actual vector image.
- New `export/playwright_exporter.py` coordinates the headless render with a
  graceful fallback message when Playwright or a Chromium browser binary is
  not installed. `PngExporter`/`SvgExporter` constructors and signatures match
  `ExportManager` so the export dialog no longer crashes.
- New `tests/export/test_playwright_exporter.py` exercises the real browser
  path (auto-skips when Playwright/Chromium is absent).

### Conversational refinement now calls the model via chat
- **`OllamaClient.chat()`** is implemented against Ollama `/api/chat` (was a
  `NotImplementedError`). Supports multi-turn messages, an optional system
  prompt, temperature, and JSON response format, with the same
  `OllamaGenerationError` error handling as `generate()`.
- **`LlmSemanticMapper.map_to_draft_with_history()`** refines a plan by
  sending prior user/assistant turns as chat history plus the structured
  refinement prompt as the final user message, so refinement is genuinely
  multi-turn and context-aware. The shared parse/validate/repair logic was
  extracted into `_parse_response` so both the generate and chat paths stay
  consistent.
- **`RefinementOrchestrator`** routes refinement through the chat path when
  conversation history is available (`_map_refinement` /
  `_conversation_history`), and falls back to the single-shot generate path
  when there is no history or the mapper does not support chat.
- New `tests/llm/test_ollama_client_chat.py`,
  `tests/llm/test_llm_semantic_mapper_chat.py`, and
  `tests/planning/test_refinement_chat_routing.py`.
- New architecture guards in `tests/architecture/test_ui_wiring.py` assert
  `chat()` no longer raises `NotImplementedError`, the refinement orchestrator
  wires chat history, and PNG/SVG exporters delegate to Playwright.

### Internal
- 541 tests; all passing (was 519).


## Unreleased

### Desktop UI wiring (follow-up to 0.12.0 known limitations)
The following library-level features are now reachable from the Tkinter app:

- **Settings dialog + persistence** ? `SettingsStore`/`SettingsManager` loaded
  in `create_app_state`; a `File -> Settings...` dialog edits the default
  renderer and default Ollama model and persists them to
  `config/app_settings.json`. The LLM-mapping toggle and model combo now
  respect saved settings on launch.
- **Gallery panel** ? gallery items load from `assets/gallery/gallery_items.json`
  at startup, a `Gallery` menu (reload / run first / run by ID) loads the
  sample dataset and prompt in one click, and a `Gallery` tab lists items.
  `GalleryRunner` now uses `ConversationState.add_user_message` so the prompt
  is actually seeded.
- **Excel (.xlsx) input** ? `File -> Load Excel...` inspects the workbook,
  prompts for a sheet when there are several, and loads it via `ExcelLoader`.
- **Multi-format export** ? `File -> Export Report HTML...` (fully working,
  titled self-contained report), plus `Export PNG...` / `Export SVG...`
  wired through `ExportManager` (graceful "not yet implemented" messages until
  the headless-renderer path lands). `PngExporter`/`SvgExporter` constructors
  and signatures now match `ExportManager` so the export dialog no longer
  crashes.
- **Style comparison** ? a `Style` menu entry runs `StyleComparator` against
  the active style and available styles, with results shown in a new
  `Style Compare` tab.

### Fixes
- **Chart.js silent trap** ? `RendererRegistry` now raises a clear `ValueError`
  for `render_target.renderer == "chartjs"` at routing time, instead of
  selecting a renderer that raises `NotImplementedError` after validation
  passes. Use the Plotly renderer.
- New `tests/architecture/test_ui_wiring.py` guards against the
  built-but-unexposed regression pattern (asserts all UI controllers are
  instantiated, settings are loaded at bootstrap, and the Chart.js path is
  rejected at routing time).

### Internal
- 519 tests; all passing (was 513).


## 0.12.0 — 2026-06-12

### New features
- **12 new built-in colour schemes** — Dark Slate, Midnight Neon, Vibrant, Colorblind Safe (Okabe-Ito), Ocean, Sunset, Forest, Pastel, Monochrome Blue, High Contrast, Solarized, and Warm Earth, on top of the original four. Selectable from the style panel and applied to charts and diagrams.
- **Image style extraction** — pick a reference image to extract a matching colour palette and style profile; optional VLM (llava, moondream, qwen-vl, etc.) enriches it with font, grid, and tone hints
- **More chart types** — histogram, box plot, heatmap, stacked bar, treemap, waterfall, funnel, radar, gauge, KPI card, rendered through Plotly
- **Mermaid diagram styles** — dark/light theme, node fill/stroke, and edge colour applied from the active style profile
- **Semantic input orchestrator** — LLM-first planning with deterministic fallback, plus a separate refinement path for adjusting an existing plan via chat
- **Recipe default styles** — recipes can carry a default style profile applied automatically on load

### Improvements
- Palette extractor now does a second-pass quantization on non-background pixels (with a saturation boost) to recover vivid data-series colours from compressed images
- Background colour estimation uses corner consensus before falling back to edge sampling
- VLM prompt now specifies a structured JSON schema; `font_category`, `grid_style`, and `label_density` are extracted and applied
- Plotly template (`plotly_dark` / `plotly_white`) now derived from background colour and applied consistently
- Default Ollama model set to `granite4:3b`
- Label density computed from edge density rather than hardcoded
- Sequence colours sorted by saturation so data-series colours appear first
- Gallery example datasets (`sales_monthly`, `height_weight`, `customers`, `regional_sales`) added under `assets/samples/`

### Internal
- 504 tests; all passing
- Renderer registry guards against unsupported renderer names at routing time
- `StyleApplier` maps all `StyleProfile` fields to `StyleIntent` including font and typography
- Removed legacy message-classifier remnants from the semantic input path

### Known limitations (built but not yet exposed in the desktop UI)
The following are implemented and unit-tested at the library level but are **not wired into the Tkinter app** in this release, and are tracked as follow-up work:
- Gallery panel (one-click example prompts + datasets)
- Settings dialog and on-disk settings persistence
- Excel (`.xlsx`) input
- Multi-format export (PNG, SVG, multi-chart report HTML) — only single-chart HTML export is wired
- Style comparison panel and style review dialog

---

## 0.11.0 — 2026-06-10

- Style review model (`EditableStyleDraft`) and review dialog
- Style comparison panel with `rank_similar_styles`
- Style import/export with built-in overwrite guard
- Vision model detector (heuristic keyword matching for VLM capability)
- Recipe default style fields (`default_style_profile_id`, `default_style_profile_name`)
- Dark/light detection improvements in Plotly and Mermaid style adapters

## 0.10.0 — 2026-06-09

- Image-based style extraction prototype (palette extraction, deterministic analysis, VLM hook)

## 0.9.0 and earlier

- Progressive scaffold: semantic mapping, LLM integration, Plotly/Mermaid renderers, recipe system, CSV loading, clarification engine, revision history
