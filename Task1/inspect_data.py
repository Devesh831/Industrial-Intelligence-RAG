"""Inspect the provided workbook without altering it.

Usage: python inspect_data.py path/to/data.xlsx
"""
import json
import sys
from pathlib import Path

import pandas as pd


def main(path):
    data = pd.read_excel(path, sheet_name="internship-data-1", engine="openpyxl")
    data["time"] = pd.to_datetime(data["time"], errors="coerce")
    sensors = data.columns.drop("time")
    numeric = data[sensors].apply(pd.to_numeric, errors="coerce")
    timestamps = data["time"].dropna()
    ordered = timestamps.drop_duplicates().sort_values()
    expected = pd.date_range(ordered.min(), ordered.max(), freq="5min")
    report = {
        "rows": len(data),
        "start": str(ordered.min()), "end": str(ordered.max()),
        "invalid_timestamps": int(data["time"].isna().sum()),
        "duplicate_timestamps": int(timestamps.duplicated().sum()),
        "off_grid_timestamps": int((ordered.dt.floor("5min") != ordered).sum()),
        "missing_grid_timestamps": int(len(expected.difference(ordered))),
        "nonnumeric_or_missing_by_sensor": numeric.isna().sum().to_dict(),
    }
    output = Path(__file__).parent / "inspection"
    output.mkdir(exist_ok=True)
    (output / "data_quality.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    numeric.describe(percentiles=[.01, .05, .5, .95, .99]).T.to_csv(output / "summary_statistics.csv")
    numeric.corr().to_csv(output / "correlation_matrix.csv")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main(sys.argv[1])
