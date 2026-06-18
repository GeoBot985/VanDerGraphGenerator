# Van Der Graph Generator

## Overview
Van Der Graph Generator is a local semantic visual-programming tool that gives users the ease of LLM-driven input while preserving the repeatability and reliability of deterministic visual rendering.

Internal package name: `semantic_visual_builder`

## Product Positioning
This project is designed for local-first visual generation from user intent, with deterministic validation and renderer adapters as the core of the system.

## Core Idea
Translate natural-language requests into a neutral visual plan, validate it deterministically, and route it to a suitable renderer.

## MVP Scope
- CSV input
- Guided visual workflow
- Local Ollama model selection
- Mermaid diagram rendering
- Plotly or Chart.js chart rendering
- Deterministic validation
- Conversational refinement
- Recipe save/load and compatibility checks
- HTML preview/export
- First-run runtime checks and environment reporting
- Image-based style extraction prototype
- Local deterministic palette extraction
- Optional local Ollama vision model support

## Architecture Summary
User request -> LLM semantic mapping -> Neutral visual plan -> Deterministic validation -> Renderer adapter -> Deterministic output

## Local Development
Use Python 3.11 or newer and install the project dependencies from `requirements.txt` and `requirements-dev.txt`.

## Running the App
```powershell
python -m semantic_visual_builder
```

Useful demo flags:

```powershell
python -m semantic_visual_builder --version
python -m semantic_visual_builder --env-report
python -m semantic_visual_builder --smoke-test
python -m semantic_visual_builder --no-llm --dataset assets/samples/sales_monthly.csv
```

## Testing
```powershell
pytest
```

## Packaging
Packaging uses the PyInstaller spec under [`build/pyinstaller/VanDerGraphGenerator.spec`](./build/pyinstaller/VanDerGraphGenerator.spec).

## Project Status
0.12.0 release candidate. The app covers CSV/Excel input, LLM semantic mapping with Ollama, deterministic validation, Mermaid and Plotly (flat + 3D) rendering, recipe save/load, HTML/PNG/SVG export, an image-based style extractor, a built-in style catalog, a gallery, and PyInstaller packaging scaffolding.

## License
MIT
