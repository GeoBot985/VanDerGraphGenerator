"""Asset manager tests."""


from semantic_visual_builder.webview.asset_manager import AssetManager


def test_local_asset_is_used_when_file_exists(tmp_path) -> None:
    vendor = tmp_path / "vendor"
    asset_path = vendor / "plotly" / "plotly.min.js"
    asset_path.parent.mkdir(parents=True)
    asset_path.write_text("console.log('plotly');", encoding="utf-8")
    manager = AssetManager(vendor)
    asset = manager.get_plotly_asset()
    assert asset.use_local is True
    assert asset.local_path == asset_path
    assert manager.asset_script_reference(asset).startswith("file:")


def test_cdn_fallback_used_when_local_asset_missing(tmp_path) -> None:
    manager = AssetManager(tmp_path / "vendor")
    asset = manager.get_mermaid_asset()
    assert asset.use_local is False
    assert asset.local_path is None
    assert asset.cdn_url.startswith("https://")


def test_script_reference_is_generated(tmp_path) -> None:
    vendor = tmp_path / "vendor"
    asset_path = vendor / "chartjs" / "chart.umd.js"
    asset_path.parent.mkdir(parents=True)
    asset_path.write_text("console.log('chartjs');", encoding="utf-8")
    manager = AssetManager(vendor)
    asset = manager.get_chartjs_asset()
    assert manager.asset_script_reference(asset).startswith("file:")


def test_missing_local_file_does_not_crash(tmp_path) -> None:
    manager = AssetManager(tmp_path / "vendor")
    assert manager.get_plotly_asset().use_local is False
