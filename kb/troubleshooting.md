# Troubleshooting

## Current limits

- Recipe remapping is intentionally basic in Sprint 5.
- Image-based look-and-feel extraction is not implemented yet.
- Advanced brand/template management is deferred to a later sprint.
- Embedded web preview may fall back to the browser.
- SVG/PNG export is limited in Sprint 6.
- Offline renderer assets must be bundled or present under `assets/vendor`.
- Style profiles are deterministic and limited to validated chart and diagram styling.
- Only renderer-safe fonts and colour values are accepted in style profiles.
- Built-in style profiles are separate from recipes and can be saved under the user style directory.
- Image style extraction falls back to deterministic palette analysis when vision support is unavailable.
- Small or low-contrast images may produce approximate style drafts.

## Common issues

- If a clarification appears, answer the pending question instead of sending a brand-new visual request.
- If a preview looks stale, regenerate it after the plan changes.
- If Ollama is disconnected, the app falls back to deterministic planning.
- If a recipe fails compatibility checks, confirm the dataset has the expected fields or apply the recipe only after loading a compatible dataset.
- If the app is packaged, bundled assets and templates must still be present in the extracted runtime resources.
- If the environment report shows missing files, rebuild the package or run from source to confirm the asset layout.
- If recipe compatibility is only partial, review the suggested field mappings before applying.
- If a recipe import fails, confirm the JSON uses schema version 2.0 and does not contain executable content.
- If a style file fails validation, confirm the schema version is 1.0 and the colour and font values are renderer-safe.
- If the style chooser is empty, refresh the available style catalog or confirm the built-in style files exist.
- If image extraction fails, confirm the file is PNG, JPG, JPEG, or WebP and that the image is readable by Pillow.
- If vision analysis is unavailable, leave the vision checkbox off and use the deterministic fallback.
