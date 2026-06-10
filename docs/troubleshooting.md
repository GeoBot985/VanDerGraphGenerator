# Troubleshooting

## Missing Assets

- Confirm the files under `assets/vendor/`, `kb/`, and `graph_matrix/` are present.
- If packaged, rebuild the executable so the bundled resources are refreshed.

## Ollama

- If Ollama is not connected, the app falls back to deterministic planning.
- Start Ollama, then use `Refresh Models`.

## Preview Issues

- Generate a valid plan before previewing.
- If the preview is stale, re-run generation after changing the plan.

## Recipes

- Recipes must match the active dataset fields to validate cleanly.
- If compatibility fails, reload the correct dataset first.
