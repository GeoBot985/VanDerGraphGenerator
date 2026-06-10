# Packaging

The desktop build uses PyInstaller and the spec in [`build/pyinstaller/VanDerGraphGenerator.spec`](../build/pyinstaller/VanDerGraphGenerator.spec).

## Source Layout

- Code runs from `src/semantic_visual_builder`.
- Bundled runtime resources live under `assets/`, `kb/`, `graph_matrix/`, and `recipes/samples/`.
- Packaged builds extract bundled resources to the runtime resource root and write user data beside the executable.

## Build Command

```powershell
scripts/build_exe.ps1
```

## Packaged Runtime

- `user_data/recipes`
- `user_data/config`
- `user_data/exports`
- `user_data/logs`

## Verification

- Run `scripts/smoke_test_source.ps1` from source.
- Run `scripts/smoke_test_dist.ps1` after packaging.
