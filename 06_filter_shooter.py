# cd "C:\Users\pcc20\test\uspsa-score"
#
# python 06_filter_shooter.py

import pandas as pd
from pathlib import Path


# ------------------------------------------------------------
# Configuration
# ------------------------------------------------------------

INPUT_FILE = Path("all_scores.xlsx")

# OUTPUT_FILE = Path("example_coder.xlsx")


# # Names to search for
# SHOOTER_NAMES = [
#     "jingyan",
#     "coder",
#     "jim wang",
# ]


# # Member numbers to search for
# MEMBER_NUMBERS = [
#     "A178525",
#     "A170259",
# ]


# OUTPUT_FILE = Path("example_david.xlsx")

# # Names to search for
# SHOOTER_NAMES = [
#     "david zhang",
#     "wei zhang",
# ]


# # Member numbers to search for
# MEMBER_NUMBERS = [
#     "FY140383",
# ]




# OUTPUT_FILE = Path("example_qian.xlsx")

# # Names to search for
# SHOOTER_NAMES = [
#     "stormtrooper",
#     "chang qian",
# ]


# # Member numbers to search for
# MEMBER_NUMBERS = [
#     "A150939",
#     "A1509",
# ]


OUTPUT_FILE = Path("example_harlan.xlsx")

# Names to search for
SHOOTER_NAMES = [
    "harlan chen",
    "chen harlan",
]


# Member numbers to search for
MEMBER_NUMBERS = [
    "A163292",
]



# ------------------------------------------------------------
# Read Excel file
# ------------------------------------------------------------

print("=" * 80)
print("Reading scores")
print("=" * 80)

print(f"Input : {INPUT_FILE}")

if not INPUT_FILE.exists():

    print()
    print(f"ERROR: File does not exist: {INPUT_FILE}")
    exit(1)


try:

    df = pd.read_excel(
        INPUT_FILE,
        engine="openpyxl"
    )

except Exception as e:

    print()
    print(f"ERROR reading Excel file: {e}")
    exit(1)


print()
print(f"Rows    : {len(df):,}")
print(f"Columns : {len(df.columns):,}")
print()


# ------------------------------------------------------------
# Check required columns
# ------------------------------------------------------------

if "Name" not in df.columns:

    print("ERROR: 'Name' column was not found.")

    print()
    print("Available columns:")

    for column in df.columns:
        print(f"  - {column}")

    exit(1)


if "Mem #" not in df.columns:

    print("ERROR: 'Mem #' column was not found.")

    print()
    print("Available columns:")

    for column in df.columns:
        print(f"  - {column}")

    exit(1)


# ------------------------------------------------------------
# Prepare search values
# ------------------------------------------------------------

name_values = [
    str(name).strip().lower()
    for name in SHOOTER_NAMES
]

member_values = [
    str(member).strip().lower()
    for member in MEMBER_NUMBERS
]


# ------------------------------------------------------------
# Create masks
# ------------------------------------------------------------

# Name:
# Contains any of the requested names, case-insensitive
name_mask = (
    df["Name"]
    .fillna("")
    .astype(str)
    .str.lower()
    .apply(
        lambda value:
            any(name in value for name in name_values)
    )
)


# Member number:
# Exact match, case-insensitive
member_mask = (
    df["Mem #"]
    .fillna("")
    .astype(str)
    .str.strip()
    .str.lower()
    .isin(member_values)
)


# ------------------------------------------------------------
# Combine filters
# ------------------------------------------------------------

filtered_df = df[
    name_mask | member_mask
].copy()


# ------------------------------------------------------------
# Show matching shooters
# ------------------------------------------------------------

print("=" * 80)
print("FILTER RESULTS")
print("=" * 80)

print()
print(f"Total rows      : {len(df):,}")
print(f"Matching rows   : {len(filtered_df):,}")

print()

if not filtered_df.empty:

    print("Matched shooters:")

    print(
        filtered_df[
            ["Name", "Mem #"]
        ]
        .drop_duplicates()
        .to_string(index=False)
    )

else:

    print("No matching shooters found.")


# ------------------------------------------------------------
# Save result
# ------------------------------------------------------------

print()
print("=" * 80)
print("Saving filtered scores")
print("=" * 80)

try:

    filtered_df.to_excel(
        OUTPUT_FILE,
        index=False,
        engine="openpyxl"
    )

except Exception as e:

    print()
    print(f"ERROR writing Excel file: {e}")
    exit(1)


# ------------------------------------------------------------
# Finished
# ------------------------------------------------------------

print()
print("=" * 80)
print("DONE")
print("=" * 80)

print(f"Output file: {OUTPUT_FILE}")
print(f"Rows       : {len(filtered_df):,}")