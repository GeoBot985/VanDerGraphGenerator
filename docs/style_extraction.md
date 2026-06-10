# Image-Based Style Extraction

## Purpose
Sprint 10 adds a prototype that converts a sample chart or diagram image into a reusable `StyleProfile`.

## What It Extracts
- Dominant colours
- Background tone
- Grid/lightness impression
- Chart tone
- Label density hint
- Basic style metadata and tags

## What It Does Not Extract
- Exact layout
- Source data
- OCR/text content
- Exact font matching
- Brand compliance judgement

## Deterministic Palette Extraction
The default path uses Pillow to load the image, sample edge pixels for a background estimate, and quantize the image to a small palette. The resulting palette is then reduced to primary, accent, and neutral style hints.

## Optional Vision Model Analysis
If a local Ollama vision-capable path is available later, the app can use it to add semantic style labels. If not, the prototype falls back to deterministic extraction.

## Saving Extracted Styles
The extracted draft is validated and can be saved as a `.style.json` file in `user_data/styles/`.

## Applying Extracted Styles
An extracted style updates only style-related fields on the current visual plan. Data roles, intent, and renderer selection remain unchanged.

## Limitations
This is an approximation. It is intended to capture look-and-feel, not recreate the original chart.

## Safety Notes
The extractor does not generate executable code and does not trust vision output without validation.
