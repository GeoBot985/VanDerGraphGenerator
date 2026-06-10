# Van Der Graph Generator

## Overview
Van Der Graph Generator is a local semantic visual-programming tool that gives users the ease of LLM-driven input while preserving the power, repeatability, and reliability of deterministic visual rendering.

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

## Architecture Summary
User request -> LLM semantic mapping -> Neutral visual plan -> Deterministic validation -> Renderer adapter -> Deterministic output

## Local Development
Use Python 3.11 or newer and install the project dependencies from `requirements.txt` and `requirements-dev.txt`.

## Running the App
```powershell
python -m semantic_visual_builder
```

## Testing
```powershell
pytest
```

## Packaging
Packaging is intentionally deferred. The repository includes a placeholder PyInstaller spec for future work.

## Project Status
Sprint 0 scaffold only. No production rendering or Ollama integration is implemented yet.

## License
MIT
