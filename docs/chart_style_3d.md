# Chart Style: Flat vs Soft 3D vs True 3D

The renderer now understands a per-plan **`chart_style`** that switches the
same chart between a flat print-friendly rendering, a soft 3D extrusion
that still reads at small sizes, and a full Plotly 3D scene with camera
tilt and lighting. The visual plan, style profile, intent mapper, and
Plotly + Mermaid renderers all share the same vocabulary.

## Values

| `chart_style` | Visual feel | Plotly output | Mermaid output |
|---------------|-------------|---------------|----------------|
| `flat` (default) | 2D rectangles, no perspective, print-friendly | Standard `bar` / `scatter` / `pie` traces | Rectangle nodes `[label]` |
| `soft_3d`       | Extruded bars / layered markers, no perspective | `bar` trace with bevel marker; splined area / line fills; gauges with thicker bars; pie pulled out slightly | Round-edge nodes `(label)` |
| `true_3d`       | Full Plotly 3D scene with tilt and lighting | `bar3d` / `scatter3d` / `surface` / `mesh3d` traces with `scene.camera`, `lighting`, `orbit` drag mode; pie exploded and rotated | Stadium / pill nodes `([label])` with shadow ring |

## Knobs

Each style profile can also expose fine-grained 3D knobs on the new
`ThreeDStyle` block (`three_d` in JSON):

| Field         | Default        | Description                                      |
|---------------|----------------|--------------------------------------------------|
| `depth`       | 12 (non-flat)  | px extrusion / bar thickness                     |
| `bevel`       | 4              | px bevel radius for the extruded edges            |
| `perspective` | 0.6 (true_3d)  | 0.0-1.0 camera perspective strength             |
| `lighting`    | `soft`         | `flat` / `soft` / `dramatic`                     |
| `shadow`      | true (non-flat)| Cast a subtle drop shadow                       |
| `tilt`        | 25 (true_3d)   | deg camera tilt (clamped to ±180)                |

The renderer clamps `tilt` / `perspective` / `depth` into their safe
ranges and the capability validator rejects negative depth and out-of-
range perspective / tilt.

## Built-in catalog

The 19 built-in styles now split into three groups so a user can pick
the right feel without writing JSON:

- **Flat / print-friendly** (the original 14): `editorial_serif`,
  `magazine_bold`, `boardroom`, `minimal_swiss`, `technical_report`,
  `academic_paper`, `dashboard_dark`, `terminal_neon`, `pastel_soft`,
  `marketing_punch`, `ocean_cool`, `sunset_warm`, `colorblind_safe`,
  `high_contrast_print`.
- **Soft 3D**: `soft_3d_gloss` (playful round bars), `soft_3d_boardroom`
  (executive deck extrusion).
- **True 3D**: `true_3d_cosmic` (dark cosmic palette + camera tilt),
  `true_3d_warehouse` (operations dashboard 3D scene), `true_3d_pastel`
  (playful pastel with gentle tilt).

`StyleApplier` copies the `three_d` block onto the visual plan, so picking
the same palette in any of the three treatments stays on-brand.

## Natural language hints

The deterministic fallback mapper recognises these phrases and translates
them into `chart_style`:

- `true 3d`, `true3d`, `immersive 3d`, `fully 3d`, `interactive 3d`,
  `3d scene` → `true_3d`
- `soft 3d`, `soft3d`, `extruded`, `raised`, plain `3d` → `soft_3d`
- `flat` → `flat`

Examples:

```
"show a true 3d bar chart of amount by region"        # bar3d scene with tilt
"plot a soft 3d heatmap"                              # heatmap with bevel + opacity
"chart the trend as a flat line"                      # 2D line, no depth
"3d scatter between height and weight"                # scatter3d
```

## Validators

- `StyleValidator` enforces `chart_style` ∈ {flat, soft_3d, true_3d},
  `lighting` ∈ {flat, soft, dramatic}, `depth >= 0`,
  `0.0 <= perspective <= 1.0`, `-180 <= tilt <= 180`.
- `CapabilityValidator` rejects true_3d when the renderer is not Plotly,
  and surfaces negative depth / out-of-range perspective as errors.

## Tests

- `tests/renderers/test_plotly_3d.py` covers the Plotly helpers and the
  bar / pie / scatter / line builders under all three styles.
- `tests/renderers/test_mermaid_3d.py` covers the Mermaid adapter shape
  swap and class-def opacity / shadow ring rules.
- `tests/planning/test_chart_style_detection.py` covers the natural-
  language 3D phrase detection.
- `tests/styles/test_three_d_style.py` covers `ThreeDStyle` round-trip,
  applier copy, summary line, and validator rules.
- `tests/validation/test_capability_3d.py` covers the capability
  validator's new 3D branches.

602 tests, all passing.
