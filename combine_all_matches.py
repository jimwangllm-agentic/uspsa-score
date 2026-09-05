# python combine_all_matches.py

import pandas as pd
from pathlib import Path

# Folder containing the club CSV files
input_folder = Path("match_links")

# Output file
output_file = Path("matches.csv")

all_matches = []

# Read every CSV in match_links
for csv_file in input_folder.glob("*.csv"):
    try:
        df = pd.read_csv(csv_file)

        # Club name = filename without .csv
        club_name = csv_file.stem

        # Keep only the columns we need
        if "match_url" not in df.columns or "match_name" not in df.columns:
            print(f"Skipping {csv_file.name}: missing match_url or match_name")
            continue

        matches = df[["match_url", "match_name"]].copy()

        # Add club name
        matches["club_name"] = club_name

        all_matches.append(matches)

        print(f"Loaded {len(matches)} matches from {csv_file.name}")

    except Exception as e:
        print(f"Error reading {csv_file.name}: {e}")

# Combine all clubs
if all_matches:
    matches_df = pd.concat(all_matches, ignore_index=True)

    # Remove duplicate matches if necessary
    matches_df = matches_df.drop_duplicates(
        subset=["match_url"]
    ).reset_index(drop=True)

    # Save
    matches_df.to_csv(output_file, index=False)

    print()
    print(f"Saved {len(matches_df)} matches to {output_file}")
else:
    print("No valid CSV files found.")