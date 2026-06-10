# Export Workflow

Van Der Graph Generator supports several export types for saving visual outputs.

## Export Types

| Type | Description |
|------|-------------|
| `html` | Raw renderer HTML preview file |
| `report_html` | Self-contained HTML with title, metadata, and chart embedded |
| `png` | PNG image (requires browser or headless renderer) |
| `svg` | SVG vector image |

## Report HTML Export

The `report_html` export wraps the chart HTML in a clean, print-ready shell:

- Document title in `<title>` and `<h1>`
- Generation timestamp
- Optional renderer name and dataset name in metadata line
- Optional notes section
- Chart HTML embedded in a bordered container

All user-supplied strings (title, dataset name) are HTML-escaped before insertion. The chart HTML is embedded verbatim — it must come from the app's own renderer output, not from user input.

**Security note:** The `content` field of an `ExportRequest` must be renderer output only. It must never contain LLM-generated strings, user-typed strings, or untrusted external content.

## ExportManager

`ExportManager.export(request: ExportRequest)` routes the request to the correct exporter:

```python
from semantic_visual_builder.export.export_manager import ExportManager, ExportRequest
from pathlib import Path

req = ExportRequest(
    export_type="report_html",
    export_dir=Path("exports"),
    content=renderer_output.content,
    title="Q4 Sales Analysis",
    renderer_name="plotly",
    dataset_name="sales_q4.csv",
)
result = ExportManager().export(req)
if result.success:
    print(f"Saved to {result.path}")
```

## File Naming

Exported files use the format: `{prefix}_{YYYYmmdd_HHMMSS}.html`

The prefix defaults to `"export"` or `"report"` but can be set via `ExportRequest.filename_prefix`.

## Limitations

- Report HTML embeds renderer JavaScript inline; it requires the original renderer library (Plotly, Chart.js, Mermaid) to be available in the output.
- PDF export is not supported.
- PNG/SVG export requires an external headless browser.
