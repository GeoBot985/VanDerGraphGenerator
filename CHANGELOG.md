# Changelog

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
