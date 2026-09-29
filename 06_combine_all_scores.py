"""

Combine PractiScore match-summary and per-stage CSV exports into Excel.

# python 06_combine_all_scores.py
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd


# ------------------------------------------------------------
# Original match-summary CSV workflow
# ------------------------------------------------------------

PARSED_FOLDER = Path("parsed")
OUTPUT_FILE = Path("all_scores.xlsx")


# ------------------------------------------------------------
# Added HTML stage-running CSV workflow
# ------------------------------------------------------------

PARSED_STAGE_RUNNINGS_FOLDER = Path("parsed_stage_runnings")
STAGE_RUNNINGS_OUTPUT_FILE = Path("all_stages.xlsx")


def combine_csv_folder(
    input_folder: Path,
    output_file: Path,
    sheet_name: str,
    sort_columns: list[str] | None = None,
) -> None:
    """Combine all CSV files in one folder into a single Excel worksheet."""
    csv_files = sorted(input_folder.glob("*.csv")) if input_folder.is_dir() else []

    print(f"Found {len(csv_files)} CSV files in {input_folder}")
    print()

    if not csv_files:
        print("No CSV files found.")
        print(f"Folder: {input_folder}")
        print()
        return

    dataframes: list[pd.DataFrame] = []
    for index, csv_file in enumerate(csv_files, start=1):
        print("=" * 80)
        print(f"File {index} of {len(csv_files)}")
        print(f"Reading: {csv_file}")
        print("=" * 80)

        try:
            # utf-8-sig supports stage-parser files and the original TXT-parser files.
            dataframe = pd.read_csv(csv_file, encoding="utf-8-sig")
        except Exception as error:
            print(f"ERROR reading {csv_file}: {error}")
            print("Skipping this file.")
            print()
            continue

        if dataframe.empty:
            print("WARNING: CSV is empty.")
            print("Skipping.")
            print()
            continue

        dataframe["source_file"] = csv_file.name
        dataframes.append(dataframe)
        print(f"Rows:    {len(dataframe):,}")
        print(f"Columns: {len(dataframe.columns):,}")
        print()

    if not dataframes:
        print("No usable CSV files were found.")
        print()
        return

    print("=" * 80)
    print("Combining CSV files...")
    print("=" * 80)
    all_scores = pd.concat(dataframes, ignore_index=True, sort=False)

    existing_sort_columns = [
        column for column in (sort_columns or []) if column in all_scores.columns
    ]
    if existing_sort_columns:
        all_scores = all_scores.sort_values(existing_sort_columns, kind="stable")

    print()
    print("Saving Excel file...")
    print(f"Output: {output_file}")
    output_file.parent.mkdir(parents=True, exist_ok=True)

    try:
        with pd.ExcelWriter(output_file, engine="openpyxl") as writer:
            all_scores.to_excel(writer, index=False, sheet_name=sheet_name)
            worksheet = writer.sheets[sheet_name]
            worksheet.freeze_panes = "A2"
            worksheet.auto_filter.ref = worksheet.dimensions
    except Exception as error:
        print()
        print(f"ERROR writing Excel file: {error}")
        print()
        return

    print()
    print("=" * 80)
    print("COMBINATION COMPLETE")
    print("=" * 80)
    print(f"CSV files processed : {len(dataframes):,}")
    print(f"Total rows          : {len(all_scores):,}")
    print(f"Total columns       : {len(all_scores.columns):,}")
    print(f"Output file         : {output_file}")
    print()


def main() -> None:
    # Original behavior: combine the TXT-parser output from parsed/.
    print("MATCH SUMMARY SCORES")
    print("=" * 80)
    combine_csv_folder(PARSED_FOLDER, OUTPUT_FILE, "All Scores")

    # Added behavior: combine the HTML stage parser's output from
    # parsed_stage_runnings/ into the requested all_stages.xlsx workbook.
    print("STAGE RUNNINGS")
    print("=" * 80)
    combine_csv_folder(
        PARSED_STAGE_RUNNINGS_FOLDER,
        STAGE_RUNNINGS_OUTPUT_FILE,
        "All Stages",
        sort_columns=[
            "match_date",
            "match_name",
            "stage_number",
            "shooter_rank_combined",
        ],
    )


if __name__ == "__main__":
    main()
