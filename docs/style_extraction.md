# Image-Based Style Extraction

## Purpose

Sprint 10 introduced the first prototype for converting a sample chart or diagram image into a reusable `StyleProfile`. Sprint 11 polishes that workflow so extracted styles can be reviewed, edited, compared, exported, and attached to recipes.

## What It Extracts

- Dominant colours (primary, secondary, accent, neutral, background)
- Background tone (light / neutral / dark) with brightness thresholds
- Text colour hint (readable contrast for the detected background)
- Grid/lightness impression
- Chart tone
- Label density hint
- Basic style metadata and tags

## What It Does Not Extract

- Exact layout or chart structure
- Source data or axis values
- OCR / text content
- Exact font matching
- Brand compliance judgement

---

## Reviewing Extracted Styles

After extraction, the app presents an **editable draft** before saving.

```
Extracted style draft:

Name:           Corporate Monthly Report
Primary:        #1f4e79
Secondary:      #5b9bd5
Accent:         #70ad47
Background:     #ffffff
Grid:           light
Label density:  medium
Tone:           corporate
```

You can edit any field before saving. Invalid hex colours or unsupported grid values block the save with a clear error message.

## Editing Extracted Colours

Every colour field (primary, secondary, accent, neutral, background, plot background, text colour) can be overridden with a hex value like `#ffc000`.

Rules:
- Hex must be `#RRGGBB` or `#RGB`.
- Background darkness is recalculated on save, so the Plotly template (dark/light) adjusts automatically.

## Dark and Light Styles

The analyzer uses brightness thresholds:

| Background brightness | Tone    | Text hint |
|-----------------------|---------|-----------|
| > 200                 | light   | `#000000` |
| < 80                  | dark    | `#ffffff` |
| otherwise             | neutral | by contrast |

Dark extracted styles configure Plotly with `plotly_dark` template and white font colour. Mermaid class definitions use readable text colour based on each fill colour.

## Comparing Similar Styles

After extraction, the app can rank existing styles by similarity:

```
Similar styles:
1. Corporate Blue — 82% — similar primary colour and light background
2. Minimal Grey — 46% — similar background but different accent
3. Presentation Green — 31% — different primary colour
```

Scores reflect: primary colour distance, background tone match, accent distance, grid match, shared tags.

Built-in styles can be compared but not overwritten by import.

## Vision-Capable Model Detection

The app uses a heuristic to detect likely vision-capable Ollama models. Models with names containing `llava`, `moondream`, `qwen-vl`, `gemma3`, etc. are flagged as likely vision-capable.

This is heuristic only — the model may still behave unexpectedly.

If the selected model does not appear vision-capable:

```
The selected model does not appear to support image input.
Deterministic palette extraction will be used.
```

## Applying Extracted Styles to Recipes

Once a style is saved, it can be set as a recipe default:

1. Load a recipe.
2. Apply the extracted style to the current chart.
3. Click **Set Active Style as Recipe Default**.
4. Save the recipe.

When the recipe is applied later, the app offers:

```
This recipe has a default style: Corporate Monthly Report.
Apply it now?
```

If the referenced style has been deleted, the recipe still applies — the style offer is simply skipped.

---

## Deterministic Palette Extraction

The default path uses Pillow to:
1. Load the image.
2. Sample edge pixels for a background estimate.
3. Quantize to a small palette (MEDIANCUT).
4. De-duplicate near-identical colours (distance threshold 22).
5. Prefer saturated non-background colours as primary.
6. Avoid white or near-black as the primary colour unless unavoidable.

## Optional Vision Model Analysis

If a vision-capable model is selected and available, it provides semantic style labels (tone, style words, suggested name). Labels are validated against an allowed-values list. Unknown values are ignored.

The app always falls back to deterministic extraction if vision analysis fails or is unavailable.

## Saving Extracted Styles

Reviewed drafts are validated and saved as `.style.json` files in `user_data/styles/`.

## Importing and Exporting

Use **Import Style** / **Export Style** in the Style panel to share `.style.json` files. Imported styles are validated before saving. Built-in styles cannot be overwritten.

## Safety Notes

- The extractor does not generate executable code.
- No Python, JavaScript, or HTML is generated from image content.
- VLM output is stored as metadata and warnings, never as trusted styling commands.
- Style profiles are validated structural data only.
