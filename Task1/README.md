# Initial workbook inspection

Run `python inspect_data.py "path/to/data.xlsx"` after installing `pandas` and `openpyxl`. The script reads the `internship-data-1` sheet and writes a quality report, summary statistics and a correlation matrix under `inspection/`. Numeric coercion counts missing or nonnumeric sensor values; it does not impute or clean them. Missing timestamps are calculated against the inclusive five-minute grid between the first and last observed timestamp.

This inspection is preliminary, not the completed assignment analysis.
