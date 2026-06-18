"""Tests for Playwright-backed PNG/SVG export.

Skip automatically when Playwright or a Chromium browser binary is missing.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from semantic_visual_builder.export.export_manager import ExportManager, ExportRequest
from semantic_visual_builder.export.playwright_exporter import PlaywrightExporter
from semantic_visual_builder.export.png_exporter import PngExporter
from semantic_visual_builder.export.svg_exporter import SvgExporter


def _can_import_playwright() -> bool:
    try:
        import playwright  # noqa: F401
        from playwright.sync_api import sync_playwright  # noqa: F401
        return True
    except ImportError:
        return False


_CAN_IMPORT = _can_import_playwright()


@pytest.fixture(scope="module")
def browser_available() -> bool:
    if not _CAN_IMPORT:
        return False
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            browser.close()
        return True
    except Exception:
        return False


def _need_browser(browser_available: bool):
    if not browser_available:
        pytest.skip("Playwright/Chromium not installed")


@pytest.fixture()
def chart_html(tmp_path: Path) -> Path:
    html = (
        "<html><body>"
        '<div id="chart">'
        '<svg xmlns="http://www.w3.org/2000/svg" width="120" height="60">'
        '<rect width="120" height="60" fill="steelblue"/>'
        '<text x="10" y="35" fill="white">Hello</text>'
        "</svg>"
        "</div></body></html>"
    )
    path = tmp_path / "preview.html"
    path.write_text(html, encoding="utf-8")
    return path


class TestPlaywrightExporter:
    def test_png_writes_image_file(
        self, chart_html: Path, tmp_path: Path, browser_available: bool
    ) -> None:
        _need_browser(browser_available)
        result = PlaywrightExporter().export_png(
            source_html_path=chart_html, export_dir=tmp_path / "out", filename_prefix="chart"
        )
        assert result.success is True
        assert result.path is not None and result.path.exists()
        assert result.path.suffix == ".png" and result.path.stat().st_size > 0

    def test_svg_writes_svg_file(
        self, chart_html: Path, tmp_path: Path, browser_available: bool
    ) -> None:
        _need_browser(browser_available)
        result = PlaywrightExporter().export_svg(
            source_html_path=chart_html, export_dir=tmp_path / "out", filename_prefix="chart"
        )
        assert result.success is True
        assert result.path is not None and result.path.exists()
        text = result.path.read_text(encoding="utf-8")
        assert "<svg" in text and text.startswith("<?xml")

    def test_missing_source_returns_failure(self, tmp_path: Path) -> None:
        result = PlaywrightExporter().export_png(
            source_html_path=tmp_path / "missing.html",
            export_dir=tmp_path / "out",
            filename_prefix="chart",
        )
        assert result.success is False
        assert "not found" in (result.error or "").lower()


class TestPngSvgExporters:
    def test_png_without_source_path_returns_clear_error(self, tmp_path: Path) -> None:
        result = PngExporter(tmp_path).export_png(source_html_path=None)
        assert result.success is False
        assert "source HTML path" in (result.error or "")

    def test_svg_without_source_path_returns_clear_error(self, tmp_path: Path) -> None:
        result = SvgExporter(tmp_path).export_svg(source_html_path=None)
        assert result.success is False
        assert "source HTML path" in (result.error or "")

    def test_png_exporter_routes_to_playwright(
        self, chart_html: Path, tmp_path: Path, browser_available: bool
    ) -> None:
        _need_browser(browser_available)
        result = PngExporter(tmp_path / "out").export_png(
            source_html_path=chart_html, filename_prefix="chart"
        )
        assert result.success is True
        assert result.path is not None and result.path.exists()

    def test_svg_exporter_routes_to_playwright(
        self, chart_html: Path, tmp_path: Path, browser_available: bool
    ) -> None:
        _need_browser(browser_available)
        result = SvgExporter(tmp_path / "out").export_svg(
            source_html_path=chart_html, filename_prefix="chart"
        )
        assert result.success is True
        assert result.path is not None and result.path.exists()


class TestExportManagerPngSvgRouting:
    def test_png_request_routes_to_png_exporter(
        self, chart_html: Path, tmp_path: Path, browser_available: bool
    ) -> None:
        _need_browser(browser_available)
        request = ExportRequest(
            export_type="png",
            export_dir=tmp_path / "out",
            filename_prefix="chart",
            extra={"source_path": str(chart_html)},
        )
        result = ExportManager().export(request)
        assert result.export_type == "png"

    def test_svg_request_routes_to_svg_exporter(
        self, chart_html: Path, tmp_path: Path, browser_available: bool
    ) -> None:
        _need_browser(browser_available)
        request = ExportRequest(
            export_type="svg",
            export_dir=tmp_path / "out",
            filename_prefix="chart",
            extra={"source_path": str(chart_html)},
        )
        result = ExportManager().export(request)
        assert result.export_type == "svg"
