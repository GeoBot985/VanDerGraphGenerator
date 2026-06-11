# Debugging LLM Usage

## Confirm Ollama is connected

- Check the app status panel.
- Look for the Ollama connection status and any reported error.

## Confirm a model is selected

- The status/debug panel shows the selected model.
- `LLM attempted` should be `yes` only when a model is selected and semantic mapping is enabled.

## Confirm the LLM was attempted

- Inspect the latest semantic trace.
- `LLM attempted` and `LLM success` are shown per request.

## Confirm fallback reason

- The trace shows `Fallback used` and `Fallback reason`.
- Fallback should never be silent.

## Inspect the latest raw LLM response

- The debug panel shows the latest raw LLM response preview when available.
- Raw prompts are not written to disk by default.

## Common failure cases

- No model selected
- Ollama unavailable
- LLM response does not pass the graph matrix contract
- unsupported visual type
