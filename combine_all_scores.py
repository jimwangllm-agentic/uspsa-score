# python -m pip install openpyxl
# python combine_all_scores.py

import pandas as pd
from pathlib import Path


# ------------------------------------------------------------
# Configuration
# ------------------------------------------------------------

PARSED_FOLDER = Path("parsed")
OUTPUT_FILE = Path("all_scores.xlsx")


# ------------------------------------------------------------
# Find all CSV files
# ------------------------------------------------------------

csv_files = sorted(PARSED_FOLDER.glob("*.csv"))

if not csv_files:
    print(f"No CSV files found in {PARSED_FOLDER}")
    exit()


print(f"Found {len(csv_files)} CSV files.")


# ------------------------------------------------------------
# Load and concatenate all CSV files
# ------------------------------------------------------------

all_data = []

for csv_file in csv_files:

    print(f"Loading: {csv_file}")

    try:
        df = pd.read_csv(csv_file)

        # Add the source filename for tracking
        df["source_file"] = csv_file.name

        all_data.append(df)

    except Exception as e:
        print(f"Error reading {csv_file}: {e}")
        continue


if not all_data:
    print("No CSV files could be loaded.")
    exit()


# ------------------------------------------------------------
# Combine all data into one table
# ------------------------------------------------------------

combined_df = pd.concat(
    all_data,
    ignore_index=True
)


# ------------------------------------------------------------
# Save to Excel
# ------------------------------------------------------------

combined_df.to_excel(
    OUTPUT_FILE,
    index=False
)


print()
print("=" * 80)
print("COMPLETED")
print("=" * 80)
print(f"Total rows : {len(combined_df)}")
print(f"Total cols : {len(combined_df.columns)}")
print(f"Output     : {OUTPUT_FILE}")