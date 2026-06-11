# LLM Semantic Mapping

## JSON contract

The LLM should return structured JSON with fields such as:

- `action`
- `visual_kind`
- `intent`
- `chart_type` or `diagram_type`
- `roles`
- `filters`
- `grouping`
- `style`
- `renderer`
- `confidence`
- `assumptions`
- `questions`

## Action values

- `create_plan`
- `refine_plan`
- `answer_capability`
- `workflow_help`
- `clarification_needed`
- `unsupported`

## Behaviour

- `create_plan` is used for initial visual planning.
- `refine_plan` is used when a current plan exists and the user wants to modify it.
- `clarification_needed` should be used when the LLM cannot safely choose a field.
- `unsupported` should be used when the requested visual is outside the graph matrix contract.

## Repair and validation

- The app may repair malformed JSON before validation.
- The draft is still validated against the graph matrix contract.
- Unsupported chart or diagram types must be rejected.
- Renderer compatibility is validated before a plan is accepted.
