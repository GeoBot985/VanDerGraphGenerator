# Graph Matrix Contract

`graph_matrix.json` is the authoritative visual contract.

## It defines

- supported visual kinds
- supported chart types
- supported diagram types
- required roles
- allowed roles
- allowed aggregations
- allowed transforms
- allowed filter operators
- renderer compatibility

## Chart types

Examples include:

- `bar`
- `horizontal_bar`
- `line`
- `scatter`
- `pie`
- `histogram`
- `box_plot`
- `heatmap`
- `stacked_bar`

## Diagram types

Examples include:

- `flowchart`
- `sequence_diagram`

## Validation rules

- unsupported visuals are rejected
- missing required roles are rejected or clarified
- invalid renderers are rejected
- unsupported aggregations and transforms are rejected
- filter operators must be contract-compliant
