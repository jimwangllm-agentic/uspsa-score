# """
# # cd "C:\Users\pcc20\uspsa-score"


# python 07_filter_shooter.py `
# --all_match_score_file all_scores.xlsx `
# --filtered_match_score_file example_coder.xlsx `
# --all_stage_score_file all_stages.xlsx `
# --filtered_stage_score_file example_stage_coder.xlsx `
# --shooter_names "jingyan,coder,jim wang" `
# --member_numbers "A178525,A170259"


# python 07_filter_shooter.py `
# --all_match_score_file all_scores.xlsx `
# --all_stage_score_file all_stages.xlsx `
# --filtered_match_score_file yanlin_matches.xlsx `
# --filtered_stage_score_file yanlin_best_stages.xlsx `
# --shooter_names "yanlin,yanlin xiang" `
# --member_numbers "A164967"


# python 07_filter_shooter.py `
# --all_match_score_file all_scores.xlsx `
# --all_stage_score_file all_stages.xlsx `
# --filtered_match_score_file john_matches.xlsx `
# --filtered_stage_score_file john_best_stages.xlsx `
# --shooter_names "john ren,ren john,ren zheng,zhen ren" `
# --member_numbers "A168570"


# python 07_filter_shooter.py `
# --all_match_score_file all_scores.xlsx `
# --all_stage_score_file all_stages.xlsx `
# --filtered_match_score_file jack_matches.xlsx `
# --filtered_stage_score_file jack_best_stages.xlsx `
# --shooter_names "jack liu,liu jack,chengchih liu,chengchih" `
# --member_numbers "L6156,TY130790,A155638"

# """


import argparse

import pandas as pd
from pathlib import Path


# ------------------------------------------------------------
# Configuration
# ------------------------------------------------------------

DEFAULT_INPUT_FILE = Path("all_scores.xlsx")
DEFAULT_OUTPUT_FILE = Path("example_coder.xlsx")
DEFAULT_STAGE_INPUT_FILE = Path("all_stages.xlsx")
DEFAULT_STAGE_OUTPUT_FILE = Path("example_stage_coder.xlsx")
DEFAULT_SHOOTER_NAMES = "jingyan,coder,jim wang"
DEFAULT_MEMBER_NUMBERS = "A178525,A170259"


# ------------------------------------------------------------
# Command-line arguments
# ------------------------------------------------------------

parser = argparse.ArgumentParser(
    description="Filter summary-score and per-stage PractiScore workbooks by shooter."
)
parser.add_argument(
    "--all_match_score_file",
    dest="summary_input",
    type=Path,
    default=DEFAULT_INPUT_FILE,
    help=f"Summary workbook to read (default: {DEFAULT_INPUT_FILE})",
)
parser.add_argument(
    "--filtered_match_score_file",
    dest="summary_output",
    type=Path,
    default=DEFAULT_OUTPUT_FILE,
    help=f"Filtered summary workbook to create (default: {DEFAULT_OUTPUT_FILE})",
)
parser.add_argument(
    "--all_stage_score_file",
    dest="stage_input",
    type=Path,
    default=DEFAULT_STAGE_INPUT_FILE,
    help=f"Stage workbook to read (default: {DEFAULT_STAGE_INPUT_FILE})",
)
parser.add_argument(
    "--filtered_stage_score_file",
    dest="stage_output",
    type=Path,
    default=DEFAULT_STAGE_OUTPUT_FILE,
    help=f"Filtered stage workbook to create (default: {DEFAULT_STAGE_OUTPUT_FILE})",
)
parser.add_argument(
    "--shooter_names",
    default=DEFAULT_SHOOTER_NAMES,
    help=f"Comma-separated shooter-name search terms (default: {DEFAULT_SHOOTER_NAMES})",
)
parser.add_argument(
    "--member_numbers",
    default=DEFAULT_MEMBER_NUMBERS,
    help=f"Comma-separated member numbers (default: {DEFAULT_MEMBER_NUMBERS})",
)
args = parser.parse_args()

INPUT_FILE = args.summary_input
OUTPUT_FILE = args.summary_output
STAGE_INPUT_FILE = args.stage_input
STAGE_OUTPUT_FILE = args.stage_output
SHOOTER_NAMES = [
    name.strip()
    for name in args.shooter_names.split(",")
    if name.strip()
]
MEMBER_NUMBERS = [
    member.strip()
    for member in args.member_numbers.split(",")
    if member.strip()
]

if not SHOOTER_NAMES and not MEMBER_NUMBERS:
    parser.error("Provide at least one shooter name or member number.")




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


# OUTPUT_FILE = Path("example_harlan.xlsx")

# # Names to search for
# SHOOTER_NAMES = [
#     "harlan chen",
#     "chen harlan",
# ]


# # Member numbers to search for
# MEMBER_NUMBERS = [
#     "A163292",
# ]



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


# ------------------------------------------------------------
# Added: filter per-stage running data
# ------------------------------------------------------------

print()
print("=" * 80)
print("Reading stage runnings")
print("=" * 80)
print(f"Input : {STAGE_INPUT_FILE}")

if not STAGE_INPUT_FILE.exists():
    print()
    print(f"ERROR: File does not exist: {STAGE_INPUT_FILE}")
    exit(1)

try:
    stage_df = pd.read_excel(
        STAGE_INPUT_FILE,
        engine="openpyxl"
    )
except Exception as e:
    print()
    print(f"ERROR reading stage Excel file: {e}")
    exit(1)

required_stage_columns = ["shooter_name", "member_number"]
missing_stage_columns = [
    column for column in required_stage_columns if column not in stage_df.columns
]

if missing_stage_columns:
    print()
    print("ERROR: Required stage columns were not found:")
    for column in missing_stage_columns:
        print(f"  - {column}")
    print()
    print("Available columns:")
    for column in stage_df.columns:
        print(f"  - {column}")
    exit(1)

stage_name_mask = (
    stage_df["shooter_name"]
    .fillna("")
    .astype(str)
    .str.lower()
    .apply(
        lambda value:
            any(name in value for name in name_values)
    )
)

stage_member_mask = (
    stage_df["member_number"]
    .fillna("")
    .astype(str)
    .str.strip()
    .str.lower()
    .isin(member_values)
)

filtered_stage_df = stage_df[
    stage_name_mask | stage_member_mask
].copy()

print()
print(f"Stage rows       : {len(stage_df):,}")
print(f"Matching rows    : {len(filtered_stage_df):,}")

if not filtered_stage_df.empty:
    print()
    print("Matched stage shooters:")
    print(
        filtered_stage_df[
            ["shooter_name", "member_number"]
        ]
        .drop_duplicates()
        .to_string(index=False)
    )
else:
    print("No matching stage shooters found.")

print()
print("=" * 80)
print("Saving filtered stage runnings")
print("=" * 80)

try:
    filtered_stage_df.to_excel(
        STAGE_OUTPUT_FILE,
        index=False,
        engine="openpyxl"
    )
except Exception as e:
    print()
    print(f"ERROR writing stage Excel file: {e}")
    exit(1)

print()
print(f"Stage output file: {STAGE_OUTPUT_FILE}")
print(f"Stage rows       : {len(filtered_stage_df):,}")
