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
PARSED_FOLDER = Path("parsed")

DOWNLOAD_SCRIPT = "download_match_scores.py"
PARSE_SCRIPT = "parse_practiscore.py"


# Create folders if they don't exist
HTML_FOLDER.mkdir(exist_ok=True)
PARSED_FOLDER.mkdir(exist_ok=True)


# ------------------------------------------------------------
# Helper: Extract match ID from URL
# ------------------------------------------------------------

def get_match_id(match_url: str) -> str:
    """
    Extract the PractiScore match ID from the URL.

    Example:
        https://practiscore.com/results/all/65e36cba-4856-4e5b-9e1c-6658aca7b997

    Returns:
        65e36cba-4856-4e5b-9e1c-6658aca7b997
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
    # Expected source files for THIS match
    # --------------------------------------------------------

    txt_file = HTML_FOLDER / f"{match_id}.txt"
    html_file = HTML_FOLDER / f"{match_id}.html"


    print("Expected source files:")

    print(f"  TXT  : {txt_file}")
    print(f"  HTML : {html_file}")


    # --------------------------------------------------------
    # Check if BOTH source files already exist
    # --------------------------------------------------------

    txt_exists = txt_file.exists() and txt_file.stat().st_size > 0
    html_exists = html_file.exists() and html_file.stat().st_size > 0


    # --------------------------------------------------------
    # Determine parsed CSV for THIS match
    # --------------------------------------------------------

    parsed_file = PARSED_FOLDER / f"{match_id}.csv"

    parsed_exists = (
        parsed_file.exists()
        and parsed_file.stat().st_size > 0
    )


    # --------------------------------------------------------
    # If parsed CSV exists, skip everything
    # --------------------------------------------------------

    if parsed_exists:

        print()
        print("Already downloaded and parsed.")
        print("Skipping download and parsing.")
        print(f"CSV: {parsed_file}")
        print()

        continue


    # --------------------------------------------------------
    # Check source files
    # --------------------------------------------------------

    if txt_exists and html_exists:

        print()
        print("Source files already exist.")
        print("Skipping download.")

        print(f"TXT : {txt_file}")
        print(f"HTML: {html_file}")

    else:

        # ----------------------------------------------------
        # Show which files are missing
        # ----------------------------------------------------

        print()

        if not txt_exists:
            print(f"TXT file missing: {txt_file}")

        else:
            print(f"TXT file exists: {txt_file}")

        if not html_exists:
            print(f"HTML file missing: {html_file}")

        else:
            print(f"HTML file exists: {html_file}")


        # ----------------------------------------------------
        # Download
        # ----------------------------------------------------

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

            print(
                f"Error running download script: {e}"
            )

            print("Skipping this match.")
            print()

            continue


        # ----------------------------------------------------
        # Wait for files to be created
        # ----------------------------------------------------

        time.sleep(0.5)


        # ----------------------------------------------------
        # Check specifically for THIS match's files
        # ----------------------------------------------------

        txt_exists = (
            txt_file.exists()
            and txt_file.stat().st_size > 0
        )

        html_exists = (
            html_file.exists()
            and html_file.stat().st_size > 0
        )


        # ----------------------------------------------------
        # Verify download
        # ----------------------------------------------------

        if not txt_exists:

            print(
                f"WARNING: Expected TXT file was not created:"
                f"\n  {txt_file}"
            )

        else:

            print(f"TXT source: {txt_file}")


        if not html_exists:

            print(
                f"WARNING: Expected HTML file was not created:"
                f"\n  {html_file}"
            )

        else:

            print(f"HTML source: {html_file}")


        # ----------------------------------------------------
        # If either source file is missing, skip
        # ----------------------------------------------------

        if not txt_exists or not html_exists:

            print(
                "Download did not produce both expected "
                "source files."
            )

            print("Skipping this match.")
            print()

            continue


    # --------------------------------------------------------
    # Parse
    # --------------------------------------------------------

    print()
    print("Parsing match...")

    try:

        result = subprocess.run(
            [
                "python",
                PARSE_SCRIPT,
                str(html_file),
                "-o",
                str(parsed_file)
            ],
            check=False
        )

        if result.returncode != 0:

            print(
                f"Parser failed with exit code "
                f"{result.returncode}"
            )

            print("Continuing to next match.")
            print()

            continue

    except Exception as e:

        print(
            f"Error running parser: {e}"
        )

        print("Continuing to next match.")
        print()

        continue


    # --------------------------------------------------------
    # Verify output
    # --------------------------------------------------------

    if (
        parsed_file.exists()
        and parsed_file.stat().st_size > 0
    ):

        print()
        print(
            f"SUCCESS: Parsed match successfully:"
            f"\n  {parsed_file}"
        )

    else:

        print()
        print(
            f"WARNING: Parser did not create a "
            f"non-empty file:"
            f"\n  {parsed_file}"
        )

    print()


# ------------------------------------------------------------
# Finished
# ------------------------------------------------------------

print("=" * 80)
print("ALL MATCHES PROCESSED")
print("=" * 80)