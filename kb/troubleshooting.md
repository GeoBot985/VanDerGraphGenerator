# Troubleshooting

## Current limits

- Recipe remapping is intentionally basic in Sprint 5.
- Image-based look-and-feel extraction is not implemented yet.
- Advanced brand/template management is deferred to a later sprint.
- Embedded web preview may fall back to the browser.
- SVG/PNG export is limited in Sprint 6.
- Offline renderer assets must be bundled or present under `assets/vendor`.

## Common issues

- If a clarification appears, answer the pending question instead of sending a brand-new visual request.
- If a preview looks stale, regenerate it after the plan changes.
- If Ollama is disconnected, the app falls back to deterministic planning.
- If a recipe fails compatibility checks, confirm the dataset has the expected fields or apply the recipe only after loading a compatible dataset.
