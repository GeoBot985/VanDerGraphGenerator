# Style Profiles

Style profiles are named, validated sets of visual settings that can be applied to charts and diagrams.

## Built-In vs User Styles

**Built-in styles** ship with the application:
- `corporate_blue` — Corporate Blue
- `minimal_grey` — Minimal Grey
- `presentation_green` — Presentation Green
- `process_blue` — Process Blue (optimised for flowcharts)

Built-in styles cannot be overwritten.

**User styles** are saved to `user_data/styles/` and can be created, edited, imported, or deleted.

## Style Profile Fields

| Field            | Description                              |
|------------------|------------------------------------------|
| `style_id`       | Unique identifier (slugified name)       |
| `style_name`     | Display name                             |
| `primary`        | Primary colour (hex)                     |
| `secondary`      | Secondary colour (hex)                   |
| `accent`         | Accent/highlight colour (hex)            |
| `neutral`        | Neutral/grey colour (hex)                |
| `background`     | Chart background colour (hex)            |
| `plot_background`| Inner plot area background (hex)         |
| `grid`           | `none` / `light` / `medium`              |
| `label_density`  | `low` / `medium` / `high`                |
| `sequence`       | Ordered list of colours for traces       |
| `tags`           | Descriptive tags for comparison          |

## Importing Styles

1. Click **Import Style** in the Style panel.
2. Select a `.style.json` file.
3. The style is validated before saving.
4. If the style ID already exists in user styles, you are asked to confirm overwrite.
5. Built-in styles cannot be overwritten by import.

## Exporting Styles

1. Select a style in the Style panel.
2. Click **Export Style**.
3. Choose a save location.
4. The style is written as a pretty-printed `.style.json` file.

Built-in styles can be exported (for inspection or as a starting point) but not re-imported over themselves.

## Recipe Default Styles

A style profile can be attached to a recipe as its default:

1. Apply the desired style to the current chart.
2. Load the desired recipe.
3. Click **Set Active Style as Recipe Default**.
4. The recipe stores `default_style_profile_id` and `default_style_profile_name`.

When the recipe is applied later, the app surfaces:

```
This recipe has a default style: Corporate Blue.
Apply it now?
```

If the referenced style is missing (deleted or not installed), the recipe still applies — the style offer is simply skipped.

To remove the default:
1. Load the recipe.
2. Click **Clear Recipe Default Style**.

## Style Comparison

When an extracted style is ready, you can compare it against existing styles. The app ranks them by similarity (0–100%).

| Score  | Label        |
|--------|--------------|
| ≥ 85%  | Very similar |
| 65–84% | Similar      |
| 40–64% | Some overlap |
| < 40%  | Different    |

Scoring factors: primary colour proximity, background tone, accent colour distance, grid style, shared tags.

Built-in styles appear in comparison results but cannot be replaced by a new import.

## Validation Rules

- `style_id` must not be blank.
- `style_name` must not be blank.
- `schema_version` must be `1.0`.
- Colour values must be `#RRGGBB` or `#RGB` hex format.
- `grid` must be `none`, `light`, or `medium`.
- `label_density` must be `low`, `medium`, or `high`.
- `legend_position` must be `right`, `bottom`, or `none`.
- `diagram.direction` must be `TD`, `LR`, `BT`, or `RL`.
- No unsafe strings (JavaScript, CSS injection, HTML tags) allowed.
