#!/usr/bin/env python3
"""
infer_schema.py — Deterministic schema inference for OKF concept generation.

Given a tabular data source (CSV, JSON, JSONL, TSV, Excel, Parquet), infers
a column-level schema (name, OKF type, nullability, uniqueness, sample
values) so that Claude doesn't have to eyeball raw data to build the
`# Schema` table in an OKF concept document.

Usage:
    python infer_schema.py <path> [--sheet SHEET_NAME] [--sample-rows N]

Output: JSON to stdout, shape:
{
  "source_path": "...",
  "detected_format": "csv" | "json" | "jsonl" | "tsv" | "excel" | "parquet",
  "row_count": 1234,
  "columns": [
    {
      "name": "order_id",
      "okf_type": "STRING",
      "pandas_dtype": "object",
      "null_count": 0,
      "null_pct": 0.0,
      "unique_count": 1234,
      "sample_values": ["A1001", "A1002", "A1003"]
    },
    ...
  ]
}

If the source is a nested JSON object (not a list of records / not
tabular), the script instead emits {"detected_format": "json_object",
"structure": <recursive key/type outline>} so Claude can decide how to
represent it (it may not map cleanly onto a single "# Schema" table).
"""

import argparse
import json
import sys
from pathlib import Path

import pandas as pd


def detect_format(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix == ".csv":
        return "csv"
    if suffix == ".tsv":
        return "tsv"
    if suffix in (".json",):
        return "json"
    if suffix in (".jsonl", ".ndjson"):
        return "jsonl"
    if suffix in (".xlsx", ".xls"):
        return "excel"
    if suffix == ".parquet":
        return "parquet"
    # Fallback: sniff content
    with open(path, "r", errors="ignore") as f:
        head = f.read(2048).strip()
    if head.startswith("{") or head.startswith("["):
        return "json"
    return "csv"


def okf_type(series: pd.Series) -> str:
    """Map a pandas dtype (with light content sniffing) to an OKF-friendly type name."""
    dtype = series.dtype
    if pd.api.types.is_bool_dtype(dtype):
        return "BOOLEAN"
    if pd.api.types.is_integer_dtype(dtype):
        return "INTEGER"
    if pd.api.types.is_float_dtype(dtype):
        return "FLOAT"
    if pd.api.types.is_datetime64_any_dtype(dtype):
        return "TIMESTAMP"
    # object dtype: sniff a sample of non-null values
    non_null = series.dropna()
    if non_null.empty:
        return "STRING"
    sample = non_null.iloc[0]
    if isinstance(sample, (list, tuple)):
        return "ARRAY"
    if isinstance(sample, dict):
        return "OBJECT"
    if isinstance(sample, bool):
        return "BOOLEAN"
    # Try parsing a slice as datetime as a heuristic (cheap, non-authoritative)
    try:
        parsed = pd.to_datetime(non_null.head(20), errors="coerce", format="mixed")
        if parsed.notna().mean() > 0.9:
            return "TIMESTAMP"
    except Exception:
        pass
    return "STRING"


def summarize_dataframe(df: pd.DataFrame, sample_rows: int) -> list:
    columns = []
    n = len(df)
    for col in df.columns:
        series = df[col]
        null_count = int(series.isna().sum())
        try:
            unique_count = int(series.nunique(dropna=True))
        except TypeError:
            unique_count = None  # unhashable types (e.g. lists/dicts)
        samples = (
            series.dropna().astype(str).head(sample_rows).tolist()
        )
        columns.append(
            {
                "name": str(col),
                "okf_type": okf_type(series),
                "pandas_dtype": str(series.dtype),
                "null_count": null_count,
                "null_pct": round(null_count / n, 4) if n else 0.0,
                "unique_count": unique_count,
                "sample_values": samples,
            }
        )
    return columns


def outline_json_object(obj, depth=0, max_depth=4):
    """Recursively describe the shape of a non-tabular JSON object."""
    if depth >= max_depth:
        return "..."
    if isinstance(obj, dict):
        return {k: outline_json_object(v, depth + 1, max_depth) for k, v in list(obj.items())[:50]}
    if isinstance(obj, list):
        if not obj:
            return []
        return [outline_json_object(obj[0], depth + 1, max_depth), f"... ({len(obj)} items)"]
    return type(obj).__name__


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("path", help="Path to the data file")
    parser.add_argument("--sheet", default=0, help="Sheet name/index for Excel files")
    parser.add_argument("--sample-rows", type=int, default=5, help="Number of sample values per column")
    args = parser.parse_args()

    path = Path(args.path)
    if not path.exists():
        print(json.dumps({"error": f"File not found: {path}"}))
        sys.exit(1)

    fmt = detect_format(path)

    try:
        if fmt == "csv":
            df = pd.read_csv(path)
        elif fmt == "tsv":
            df = pd.read_csv(path, sep="\t")
        elif fmt == "excel":
            df = pd.read_excel(path, sheet_name=args.sheet)
        elif fmt == "parquet":
            df = pd.read_parquet(path)
        elif fmt == "jsonl":
            df = pd.read_json(path, lines=True)
        elif fmt == "json":
            raw = json.loads(path.read_text())
            if isinstance(raw, list):
                df = pd.json_normalize(raw)
            elif isinstance(raw, dict):
                # Look for a single top-level list of records (common API envelope)
                list_fields = [k for k, v in raw.items() if isinstance(v, list) and v and isinstance(v[0], dict)]
                if len(list_fields) == 1:
                    df = pd.json_normalize(raw[list_fields[0]])
                    fmt = f"json (records field: {list_fields[0]})"
                else:
                    print(
                        json.dumps(
                            {
                                "source_path": str(path),
                                "detected_format": "json_object",
                                "note": "Top-level JSON is an object, not a list of records — not directly tabular. "
                                        "Structure outline below; represent as nested fields in the OKF Schema "
                                        "section, or split into multiple concepts if it contains multiple entities.",
                                "structure": outline_json_object(raw),
                            },
                            indent=2,
                        )
                    )
                    return
            else:
                print(json.dumps({"error": "Top-level JSON is a scalar, not tabular data."}))
                sys.exit(1)
        else:
            print(json.dumps({"error": f"Unsupported format: {fmt}"}))
            sys.exit(1)
    except Exception as e:
        print(json.dumps({"error": f"Failed to read {path} as {fmt}: {e}"}))
        sys.exit(1)

    result = {
        "source_path": str(path),
        "detected_format": fmt,
        "row_count": int(len(df)),
        "columns": summarize_dataframe(df, args.sample_rows),
    }
    print(json.dumps(result, indent=2, default=str))


if __name__ == "__main__":
    main()
