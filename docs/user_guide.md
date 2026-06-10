# User Guide

## Start Here

Run the app from source:

```powershell
python -m semantic_visual_builder
```

## Common Tasks

- Load a CSV with `File -> Load CSV` or `File -> Load Sample Dataset`.
- Describe the visual goal in the chat panel.
- Review the plan, validation, and preview panes.
- Save a recipe after the plan is valid.
- Load a recipe to reuse a prior visual structure.

## Demo Controls

- `View -> Show Environment Report` displays runtime paths and app state.
- `View -> Open Logs Folder` opens the writable log directory.
- `View -> Open Exports Folder` opens generated HTML previews.
- `Help -> About` shows version and build information.

## Runtime Flags

- `--version` prints the release version.
- `--env-report` prints the environment summary.
- `--smoke-test` runs the first-run checks and exits with a status code.
