# cd "C:\Users\pcc20\test\uspsa-score"
#
# python 03_download_all_matches.py

import pandas as pd
import subprocess
from pathlib import Path
import time
from urllib.parse import urlparse


# ------------------------------------------------------------
# Configuration
# ------------------------------------------------------------

MATCHES_FILE = Path("matches.csv")
HTML_FOLDER = Path("html_sources")

DOWNLOAD_SCRIPT = "download_match_scores.py"


# Create folder if it doesn't exist
HTML_FOLDER.mkdir(exist_ok=True)


# ------------------------------------------------------------
# Helper: Extract match ID from URL
# ------------------------------------------------------------

def get_match_id(match_url: str) -> str:
    """
    Extract the PractiScore match ID from the URL.
    """

    parsed_url = urlparse(match_url)

    match_id = parsed_url.path.rstrip("/").split("/")[-1]

    if not match_id:
        raise ValueError(
            f"Could not extract match ID from URL: {match_url}"
        )

    return match_id


# ------------------------------------------------------------
# Load matches.csv
# ------------------------------------------------------------

df = pd.read_csv(MATCHES_FILE)

print(f"Loaded {len(df)} matches from {MATCHES_FILE}")
print()


# ------------------------------------------------------------
# Process every match
# ------------------------------------------------------------

for index, row in df.iterrows():

    match_url = str(row["match_url"]).strip()
    match_name = str(row.get("match_name", "")).strip()
    club_name = str(row.get("club_name", "")).strip()

    # --------------------------------------------------------
    # Extract Match ID
    # --------------------------------------------------------

    try:

        match_id = get_match_id(match_url)

    except Exception as e:

        print(f"ERROR: {e}")
        print("Skipping this match.")
        print()

        continue


    print("=" * 80)
    print(f"Match {index + 1} of {len(df)}")
    print(f"Club     : {club_name}")
    print(f"Match    : {match_name}")
    print(f"Match ID : {match_id}")
    print(f"URL      : {match_url}")
    print("=" * 80)


    # --------------------------------------------------------
    # Expected source files
    # --------------------------------------------------------

    txt_file = HTML_FOLDER / f"{match_id}.txt"
    html_file = HTML_FOLDER / f"{match_id}.html"

    print()
    print("Expected source files:")
    print(f"  TXT  : {txt_file}")
    print(f"  HTML : {html_file}")


    # --------------------------------------------------------
    # Check existing files
    # --------------------------------------------------------

    txt_exists = (
        txt_file.exists()
        and txt_file.stat().st_size > 0
    )

    html_exists = (
        html_file.exists()
        and html_file.stat().st_size > 0
    )


    # --------------------------------------------------------
    # Skip if both files already exist
    # --------------------------------------------------------

    if txt_exists and html_exists:

        print()
        print("Source files already exist.")
        print("Skipping download.")
        print()

        continue


    # --------------------------------------------------------
    # Show missing files
    # --------------------------------------------------------

    print()

    if txt_exists:
        print(f"TXT file exists : {txt_file}")
    else:
        print(f"TXT file missing: {txt_file}")

    if html_exists:
        print(f"HTML file exists : {html_file}")
    else:
        print(f"HTML file missing: {html_file}")


    # --------------------------------------------------------
    # Download
    # --------------------------------------------------------

    print()
    print("Downloading match...")

    try:

        result = subprocess.run(
            [
                "python",
                DOWNLOAD_SCRIPT,
                match_url
            ],
            check=False
        )

        if result.returncode != 0:

            print(
                f"Download failed with exit code "
                f"{result.returncode}"
            )

            print("Skipping this match.")
            print()

            continue

    except Exception as e:

        print(f"Error running download script: {e}")

        print("Skipping this match.")
        print()

        continue


    # --------------------------------------------------------
    # Wait briefly for files
    # --------------------------------------------------------

    time.sleep(0.5)


    # --------------------------------------------------------
    # Verify downloaded files
    # --------------------------------------------------------

    txt_exists = (
        txt_file.exists()
        and txt_file.stat().st_size > 0
    )

    html_exists = (
        html_file.exists()
        and html_file.stat().st_size > 0
    )


    if txt_exists:
        print(f"TXT source : {txt_file}")
    else:
        print(
            f"WARNING: TXT file was not created:\n"
            f"  {txt_file}"
        )


    if html_exists:
        print(f"HTML source: {html_file}")
    else:
        print(
            f"WARNING: HTML file was not created:\n"
            f"  {html_file}"
        )


    # --------------------------------------------------------
    # Verify both files
    # --------------------------------------------------------

    if not txt_exists or not html_exists:

        print()
        print(
            "Download did not produce both expected "
            "source files."
        )

        print("Skipping this match.")
        print()

        continue


    print()
    print("Download successful.")
    print()


# ------------------------------------------------------------
# Finished
# ------------------------------------------------------------

print("=" * 80)
print("ALL MATCHES DOWNLOADED")
print("=" * 80)