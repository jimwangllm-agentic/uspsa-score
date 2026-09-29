"""Select each shooter's best-ranked stage run from the filtered stage workbook."""

# python 08_select_best_stage_run.py example_stage_coder.xlsx example_stage_best_run_coder.xlsx

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


INPUT_FILE = Path("example_stage_coder.xlsx")
OUTPUT_FILE = Path("example_stage_best_run_code.xlsx")

# A lower numeric rank is better. The HTML parser supplies this overall rank
# across all divisions; change it to shooter_rank_division for division-only
# best runs.
RANK_COLUMN = "shooter_rank_combined"
PERCENT_COLUMN = "shooter_percent_combined"
GROUP_COLUMNS = ["match_id", "shooter_name", "member_number"]


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Select the best-ranked stage run per shooter and match."
    )
    parser.add_argument(
        "input_file",
        type=Path,
        nargs="?",
        default=INPUT_FILE,
        help=f"Filtered stage workbook to read (default: {INPUT_FILE})",
    )
    parser.add_argument(
        "output_file",
        type=Path,
        nargs="?",
        default=OUTPUT_FILE,
        help=f"Workbook to create (default: {OUTPUT_FILE})",
    )
    args = parser.parse_args()

    print("=" * 80)
    print("SELECT BEST STAGE RUN PER MATCH")
    print("=" * 80)
    print(f"Input : {args.input_file}")
    print(f"Output: {args.output_file}")

    if not args.input_file.exists():
        print()
        print(f"ERROR: File does not exist: {args.input_file}")
        return 1

    try:
        stage_runs = pd.read_excel(args.input_file, engine="openpyxl")
    except Exception as error:
        print()
        print(f"ERROR reading Excel file: {error}")
        return 1

    required_columns = GROUP_COLUMNS + [RANK_COLUMN]
    missing_columns = [
        column for column in required_columns if column not in stage_runs.columns
    ]
    if missing_columns:
        print()
        print("ERROR: Required columns were not found:")
        for column in missing_columns:
            print(f"  - {column}")
        return 1

    # Invalid/missing ranks are not scored stage runs and cannot be a best run.
    stage_runs["_rank"] = pd.to_numeric(stage_runs[RANK_COLUMN], errors="coerce")
    ranked_runs = stage_runs.dropna(subset=["_rank"]).copy()

    if ranked_runs.empty:
        print()
        print(f"ERROR: No numeric values were found in {RANK_COLUMN!r}.")
        return 1

    # For equally ranked runs, retain the higher percent; then choose the first
    # stage number as a stable final tie-breaker.
    sort_columns = GROUP_COLUMNS + ["_rank"]
    ascending = [True] * len(GROUP_COLUMNS) + [True]
    if PERCENT_COLUMN in ranked_runs.columns:
        ranked_runs["_percent"] = pd.to_numeric(
            ranked_runs[PERCENT_COLUMN], errors="coerce"
        ).fillna(-1)
        sort_columns.append("_percent")
        ascending.append(False)
    if "stage_number" in ranked_runs.columns:
        ranked_runs["_stage_number"] = pd.to_numeric(
            ranked_runs["stage_number"], errors="coerce"
        ).fillna(float("inf"))
        sort_columns.append("_stage_number")
        ascending.append(True)

    best_runs = (
        ranked_runs.sort_values(sort_columns, ascending=ascending, kind="stable")
        .groupby(GROUP_COLUMNS, as_index=False, dropna=False)
        .first()
        .drop(columns=["_rank", "_percent", "_stage_number"], errors="ignore")
    )

    preferred_columns = [
        column
        for column in (
            "match_date",
            "match_name",
            "stage_number",
            "stage_name",
            "shooter_name",
            "member_number",
            RANK_COLUMN,
            PERCENT_COLUMN,
            "shooter_rank_division",
            "shooter_percent_division",
            "division",
            "class",
            "hit_factor",
            "time",
            "stage_points",
        )
        if column in best_runs.columns
    ]
    remaining_columns = [
        column for column in best_runs.columns if column not in preferred_columns
    ]
    best_runs = best_runs[preferred_columns + remaining_columns]

    try:
        args.output_file.parent.mkdir(parents=True, exist_ok=True)
        with pd.ExcelWriter(args.output_file, engine="openpyxl") as writer:
            best_runs.to_excel(writer, sheet_name="Best Stage Runs", index=False)
            worksheet = writer.sheets["Best Stage Runs"]
            worksheet.freeze_panes = "A2"
            worksheet.auto_filter.ref = worksheet.dimensions
    except Exception as error:
        print()
        print(f"ERROR writing Excel file: {error}")
        return 1

    print()
    print(f"Input stage rows : {len(stage_runs):,}")
    print(f"Best runs saved  : {len(best_runs):,}")
    print(f"Output file      : {args.output_file}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
