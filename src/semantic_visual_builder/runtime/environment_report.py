"""Build human-readable environment reports."""

from __future__ import annotations

from semantic_visual_builder.state.app_state import AppState

from .runtime_paths import RuntimePaths


def build_environment_report(runtime_paths: RuntimePaths, app_state: AppState) -> str:
    ollama_connected = (
        app_state.ollama_status.is_connected if app_state.ollama_status else False
    )
    dataset_loaded = app_state.dataset_context.loaded_dataset is not None
    if app_state.last_preview_path is None and app_state.last_html_build_warnings == []:
        renderer_asset_status = "not generated yet"
    elif app_state.last_html_build_warnings:
        renderer_asset_status = "warnings present"
    else:
        renderer_asset_status = "local assets enabled"
    lines = [
        "Environment report",
        f"App: {runtime_paths.app_root.name}",
        f"Packaged mode: {'yes' if runtime_paths.is_packaged else 'no'}",
        f"App root: {runtime_paths.app_root}",
        f"Resource root: {runtime_paths.resource_root}",
        f"Asset dir: {runtime_paths.asset_dir}",
        f"Export dir: {runtime_paths.export_dir}",
        f"Log dir: {runtime_paths.log_dir}",
        f"Ollama connected: {ollama_connected}",
        f"Selected model: {app_state.model_registry.selected_model or 'None'}",
        f"Available model count: {len(app_state.model_registry.models)}",
        f"Renderer asset status: {renderer_asset_status}",
        f"Dataset loaded: {'yes' if dataset_loaded else 'no'}",
    ]
    return "\n".join(lines)
