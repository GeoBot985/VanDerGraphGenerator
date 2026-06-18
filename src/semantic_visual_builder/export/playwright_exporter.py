"""Playwright-based static export of generated chart HTML.

Renders a standalone preview HTML file in a headless Chromium browser and
either screenshots the chart container (PNG) or extracts the rendered SVG
node (SVG). Playwright and a Chromium browser binary are required; if either
is missing the exporter returns a graceful failure instead of raising.
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from .export_result import ExportResult

_CHART_SELECTOR = "#chart"
_DIAGRAM_SELECTOR = ".mermaid"
_VIEWPORT_WIDTH = 1280
_VIEWPORT_HEIGHT = 720
_RENDER_WAIT_MS = 1500


class PlaywrightExporter:
    """Render preview HTML to PNG or extract SVG using headless Chromium."""

    def export_png(
        self,
        source_html_path: Path | str,
        export_dir: Path,
        filename_prefix: str = "chart",
    ) -> ExportResult:
        return self._run(
            kind="png",
            source_html_path=Path(source_html_path),
            export_dir=export_dir,
            filename_prefix=filename_prefix,
        )

    def export_svg(
        self,
        source_html_path: Path | str,
        export_dir: Path,
        filename_prefix: str = "chart",
    ) -> ExportResult:
        return self._run(
            kind="svg",
            source_html_path=Path(source_html_path),
            export_dir=export_dir,
            filename_prefix=filename_prefix,
        )

    def _run(
        self,
        kind: str,
        source_html_path: Path,
        export_dir: Path,
        filename_prefix: str,
    ) -> ExportResult:
        if not source_html_path.exists():
            return ExportResult(
                success=False,
                export_type=kind,
                error=f"Source HTML not found: {source_html_path}",
            )
        try:
            from playwright.sync_api import sync_playwright
        except ImportError:
            return ExportResult(
                success=False,
                export_type=kind,
                error=(
                    "Playwright is not installed. Install the 'playwright' "
                    "package and run `python -m playwright install chromium`."
                ),
            )
        export_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        safe_prefix = _safe_filename(filename_prefix) or kind
        target_path = export_dir / f"{safe_prefix}_{timestamp}.{kind}"
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                try:
                    page = browser.new_page(
                        viewport={"width": _VIEWPORT_WIDTH, "height": _VIEWPORT_HEIGHT}
                    )
                    page.goto(source_html_path.resolve().as_uri())
                    self._wait_for_chart(page)
                    if kind == "png":
                        self._screenshot(page, target_path)
                    else:
                        svg_text = self._extract_svg(page)
                        if svg_text is None:
                            return ExportResult(
                                success=False,
                                export_type="svg",
                                error=(
                                    "No <svg> node found in the rendered chart. "
                                    "SVG export is supported for Plotly and Mermaid "
                                    "outputs."
                                ),
                            )
                        target_path.write_text(svg_text, encoding="utf-8")
                finally:
                    browser.close()
            return ExportResult(success=True, path=target_path, export_type=kind)
        except Exception as exc:
            return ExportResult(success=False, export_type=kind, error=str(exc))

    def _wait_for_chart(self, page) -> None:
        # Wait for network-level rendering to settle, then give JS renderers
        # (Plotly/Mermaid) a short grace period to inject their SVG nodes.
        try:
            page.wait_for_load_state("networkidle", timeout=15000)
        except Exception:
            pass
        selector = f"{_CHART_SELECTOR}, {_DIAGRAM_SELECTOR}"
        try:
            page.wait_for_selector(selector, timeout=10000)
        except Exception:
            pass
        page.wait_for_timeout(_RENDER_WAIT_MS)

    def _screenshot(self, page, target_path: Path) -> None:
        # Prefer the chart element; fall back to full page if it is missing.
        chart = page.query_selector(_CHART_SELECTOR)
        if chart is None:
            chart = page.query_selector(_DIAGRAM_SELECTOR)
        if chart is not None:
            chart.screenshot(path=str(target_path))
        else:
            page.screenshot(path=str(target_path), full_page=True)

    def _extract_svg(self, page) -> str | None:
        # Plotly renders svg inside #chart; Mermaid renders svg inside .mermaid.
        svg = page.query_selector(f"{_CHART_SELECTOR} svg")
        if svg is None:
            svg = page.query_selector(f"{_DIAGRAM_SELECTOR} svg")
        if svg is None:
            svg = page.query_selector("body svg")
        if svg is None:
            return None
        outer = svg.evaluate("el => el.outerHTML")
        if not outer or "<svg" not in outer:
            return None
        return '<?xml version="1.0" encoding="UTF-8" standalone="no"?>\n' + outer


def _safe_filename(text: str) -> str:
    safe = "".join(c if c.isalnum() or c in ("-", "_") else "_" for c in text)
    return safe.strip("_")
