# cd "C:\Users\pcc20\test\uspsa-score"
#
# python 05_combine_all_scores.py

import subprocess
from pathlib import Path


# ------------------------------------------------------------
# Configuration
# ------------------------------------------------------------

HTML_FOLDER = Path("html_sources")
PARSED_FOLDER = Path("parsed")

PARSE_SCRIPT = "parse_practiscore.py"


# Create parsed folder if it doesn't exist
PARSED_FOLDER.mkdir(exist_ok=True)


# ------------------------------------------------------------
# Find downloaded HTML files
# ------------------------------------------------------------

html_files = sorted(HTML_FOLDER.glob("*.html"))

print(
    f"Found {len(html_files)} HTML files "
    f"in {HTML_FOLDER}"
)
print()


# ------------------------------------------------------------
# Process each HTML file
# ------------------------------------------------------------

for index, html_file in enumerate(html_files, start=1):

    # --------------------------------------------------------
    # Extract match ID from filename
    #
    # Example:
    #
    # 65e36cba-4856-4e5b-9e1c-6658aca7b997.html
    #
    # -> 65e36cba-4856-4e5b-9e1c-6658aca7b997
    # --------------------------------------------------------

    match_id = html_file.stem

    parsed_file = PARSED_FOLDER / f"{match_id}.csv"


    print("=" * 80)
    print(f"Match {index} of {len(html_files)}")
    print(f"Match ID : {match_id}")
    print(f"HTML     : {html_file}")
    print(f"CSV      : {parsed_file}")
    print("=" * 80)


    # --------------------------------------------------------
    # Verify HTML file
    # --------------------------------------------------------

    if (
        not html_file.exists()
        or html_file.stat().st_size == 0
    ):

        print()
        print("HTML file is missing or empty.")
        print("Skipping.")
        print()

        continue


    # --------------------------------------------------------
    # Skip if already parsed
    # --------------------------------------------------------

    if (
        parsed_file.exists()
        and parsed_file.stat().st_size > 0
    ):

        print()
        print("Already parsed.")
        print("Skipping.")

        print(f"CSV: {parsed_file}")
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

    except Exception as e:

        print()
        print(f"Error running parser: {e}")
        print("Continuing to next match.")
        print()

        continue


    # --------------------------------------------------------
    # Check parser return code
    # --------------------------------------------------------

    if result.returncode != 0:

        print()
        print(
            f"Parser failed with exit code "
            f"{result.returncode}"
        )

        print("Continuing to next match.")
        print()

        continue


    # --------------------------------------------------------
    # Verify parsed CSV
    # --------------------------------------------------------

    if (
        parsed_file.exists()
        and parsed_file.stat().st_size > 0
    ):

        print()
        print("SUCCESS: Parsed match successfully.")
        print(f"CSV: {parsed_file}")

    else:

        print()
        print(
            "WARNING: Parser did not create a "
            "non-empty CSV file."
        )

        print(f"Expected: {parsed_file}")


    print()


# ------------------------------------------------------------
# Finished
# ------------------------------------------------------------

print("=" * 80)
print("ALL DOWNLOADED MATCHES PARSED")
print("=" * 80)