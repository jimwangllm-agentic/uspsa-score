# cd "C:\Users\pcc20\test\uspsa-score"

# python 05_combine_all_scores.py

import pandas as pd
from pathlib import Path


# ------------------------------------------------------------
# Configuration
# ------------------------------------------------------------

PARSED_FOLDER = Path("parsed")
OUTPUT_FILE = Path("all_scores.xlsx")


# ------------------------------------------------------------
# Find CSV files
# ------------------------------------------------------------

csv_files = sorted(PARSED_FOLDER.glob("*.csv"))

print(
    f"Found {len(csv_files)} CSV files "
    f"in {PARSED_FOLDER}"
)
print()


# ------------------------------------------------------------
# Check if any files exist
# ------------------------------------------------------------

if not csv_files:

    print("No CSV files found.")
    print(f"Folder: {PARSED_FOLDER}")
    exit()


# ------------------------------------------------------------
# Read and combine all CSV files
# ------------------------------------------------------------

dataframes = []

for index, csv_file in enumerate(csv_files, start=1):

    print("=" * 80)
    print(f"File {index} of {len(csv_files)}")
    print(f"Reading: {csv_file}")
    print("=" * 80)

    try:

        df = pd.read_csv(csv_file)

        # Skip empty CSV files
        if df.empty:

            print("WARNING: CSV is empty.")
            print("Skipping.")
            print()

            continue


        # ----------------------------------------------------
        # Add source file
        # ----------------------------------------------------

        df["source_file"] = csv_file.name


        # ----------------------------------------------------
        # Add to list
        # ----------------------------------------------------

        dataframes.append(df)

        print(f"Rows:    {len(df):,}")
        print(f"Columns: {len(df.columns):,}")
        print()

    except Exception as e:

        print(
            f"ERROR reading {csv_file}: {e}"
        )

        print("Skipping this file.")
        print()


# ------------------------------------------------------------
# Check if anything was loaded
# ------------------------------------------------------------

if not dataframes:

    print("No usable CSV files were found.")
    exit()


# ------------------------------------------------------------
# Combine all DataFrames
# ------------------------------------------------------------

print("=" * 80)
print("Combining CSV files...")
print("=" * 80)

all_scores = pd.concat(
    dataframes,
    ignore_index=True,
    sort=False
)


# ------------------------------------------------------------
# Save Excel file
# ------------------------------------------------------------

print()
print("Saving Excel file...")
print(f"Output: {OUTPUT_FILE}")

try:

    all_scores.to_excel(
        OUTPUT_FILE,
        index=False,
        engine="openpyxl"
    )

except Exception as e:

    print()
    print(f"ERROR writing Excel file: {e}")
    exit(1)


# ------------------------------------------------------------
# Summary
# ------------------------------------------------------------

print()
print("=" * 80)
print("COMBINATION COMPLETE")
print("=" * 80)

print(f"CSV files processed : {len(dataframes):,}")
print(f"Total rows          : {len(all_scores):,}")
print(f"Total columns       : {len(all_scores.columns):,}")
print(f"Output file         : {OUTPUT_FILE}")

print()
print("Columns:")
for column in all_scores.columns:
    print(f"  - {column}")

print()
print("=" * 80)