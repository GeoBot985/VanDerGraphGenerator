# Changelog

## Unreleased (3D + flat style mix)

### 3D effects can now coexist with flat styles

The Plotly and Mermaid renderers understand a new `chart_style` knob on the
visual plan: `flat` (default, the existing behaviour), `soft_3d` (extruded
bars / layered markers but still 2D layout), and `true_3d` (full Plotly 3D
scene with camera tilt and lighting). The same style profile can therefore
produce a flat, soft_3d, or true_3d render of the same chart without
changing any data or role wiring.

- **Visual plan schema** now carries `chart_style`, `depth`, `bevel`,
  `perspective`, `lighting`, `shadow`, and `tilt` on `StyleIntent`. The
  visual plan helpers (`apply_3d_to_style`, `summarise_style_3d`,
  `merge_visual_plans`, `visual_plan_from_dict`, `visual_plan_from_llm_draft`)
  preserve the new fields end-to-end.
- **Style profile schema** gains a sibling `ThreeDStyle` block (`three_d` in
  JSON). `StyleApplier` copies `chart_style` plus depth / bevel / perspective
  / lighting / shadow / tilt onto the visual plan, leaving existing flat
  styles untouched when the profile does not opt in.
- **Style profile validator** rejects unknown `chart_style` / `lighting`
  values, negative depth / bevel, out-of-range `perspective`, and
  `tilt` outside ±180. `StyleSummary` surfaces the 3D treatment in the
  panel summary, and `StyleComparator` weighs it into the similarity score.
- **Built-in style catalog** has grown to 19 profiles: the original 14 flat
  styles plus `soft_3d_gloss`, `soft_3d_boardroom`, `true_3d_cosmic`,
  `true_3d_warehouse`, and `true_3d_pastel`. All three treatments share the
  same palette families so picking "Magazine Bold" in soft_3d feels like a
  natural extension of the flat "Magazine Bold".
- **Plotly renderer** (`renderers/plotly_3d.py`) routes `chart_style`
  through the existing chart builders: bars / pies / scatter / line /
  area / bubble / heatmap / treemap / waterfall / funnel / radar / gauge
  / histogram / box / stacked bar / stacked area each emit a `bar3d`,
  `scatter3d`, `surface`, `mesh3d`, exploded `pie`, or layered marker
  shape when the user asks for 3D, and fall back to the flat trace
  otherwise. A reusable `scene()` helper configures the camera, lighting
  and orbit drag mode for `true_3d` scenes.
- **Mermaid renderer** maps `chart_style` to node shapes: rectangles for
  `flat`, round-edge nodes for `soft_3d`, and stadium / pill shapes for
  `true_3d`. `MermaidStyleAdapter` adds fill-opacity, thicker strokes,
  and a subtle shadow on the `classDef` rules so the same colourway reads
  as layered or cylinder-shaped.
- **Intent mapping** recognises natural-language 3D cues. Requests like
  "show a true 3d bar chart", "immersive 3d scatter", or "extruded pie
  chart" now propagate `chart_style` onto the resulting visual plan; a
  bare "3d" stays on the cheaper `soft_3d` extrusion.
- **Capability validator** flags true_3d plans routed through non-Plotly
  renderers and rejects negative depth / out-of-range perspective / tilt.
- 602 tests, all passing (37 new tests cover the renderer, style schema,
  capability, planner, and built-in catalog paths).

## Unreleased (composite built-in styles)

### Built-in styles are now full design systems, not just colour schemes
The previous built-in colour-scheme styles (corporate_blue, minimal_grey,
dark_slate, ocean, etc.) have been removed and replaced with 14 composite
styles. Each style combines a colour palette **with a typographic identity**
(font family, weight, title/label/tick sizes) **and a chart surface
treatment** (background, plot background, grid, legend position, label
density, title alignment, bar gap, line shape), so switching a style changes
the whole feel of a chart or diagram, not just its data colours.
