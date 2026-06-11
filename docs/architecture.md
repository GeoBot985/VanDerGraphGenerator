# Architecture

## System model

- LLM owns user input interpretation.
- Graph matrix owns the visual contract.
- Deterministic code owns validation, rendering, schema matching, and fallback safety.

## Request flow

1. A chat message enters `SemanticInputOrchestrator`.
2. The orchestrator attempts LLM semantic mapping when LLM mapping is enabled and a model is selected.
3. The resulting draft is validated against `graph_matrix.json`.
4. If the LLM output is valid, the plan is applied.
5. If the LLM output is unsupported, the request is rejected with an explicit unsupported response.
6. If LLM mapping is unavailable, limited deterministic fallback can be used and is labeled as such.

## Deterministic code is still allowed for

- contract validation
- schema matching
- field mapping fallback
- structured patch application
- renderer selection and safety
- recipe compatibility

## Deterministic code is not the primary input router

- `MessageClassifier` is removed from the active UI path.
- Keyword-style refinement parsing is not the normal architecture.
- `graph_matrix.json` is the source of truth for supported visuals and roles.
