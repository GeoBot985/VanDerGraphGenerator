# Excel Input

Van Der Graph Generator accepts `.xlsx` files as dataset input in addition to CSV files.

## Supported Format

- **Format:** `.xlsx` (Excel Open XML)
- **Engine:** `openpyxl`
- **Not supported:** `.xls`, `.xlsm`, `.xlsb`, password-protected workbooks

## Worksheet Selection

When an `.xlsx` file contains multiple worksheets, the app inspects the workbook and presents the available sheet names. The user selects one sheet before the data is loaded.

`ExcelLoader.inspect_workbook(path)` returns an `ExcelWorkbookInfo` containing:

```
ExcelWorkbookInfo(path=..., sheet_names=["Sheet1", "Sales Q4", "Reference"])
```

`ExcelLoader.load_sheet(path, sheet_name)` loads the selected sheet into a `LoadedExcelDataset`:

```
LoadedExcelDataset(path=..., sheet_name="Sales Q4", dataframe=<DataFrame>)
```

Column names are automatically stripped of leading/trailing whitespace.

## Dataset Source Tracking

When an Excel file is loaded, `DatasetSourceInfo` records:

```python
DatasetSourceInfo(source_type="excel", path=Path("data.xlsx"), sheet_name="Sales Q4")
```

This is stored in `DatasetContext.source_info` and shown in the UI.

## Limitations

- Only one worksheet can be active at a time.
- The first worksheet is used automatically if the user does not explicitly select one.
- Merged cells and complex formatting are flattened by `openpyxl`.
- Macro-enabled workbooks (`.xlsm`) are not supported.
