from pathlib import Path
import subprocess
import sys


# ------------------------------------------------------------
# Configuration
# ------------------------------------------------------------

HTML_FOLDER = Path("html_sources")
PARSED_FOLDER = Path("parsed")
PARSE_SCRIPT = Path("parse_practiscore.py")


# ------------------------------------------------------------
# Create output folder
# ------------------------------------------------------------

PARSED_FOLDER.mkdir(parents=True, exist_ok=True)


# ------------------------------------------------------------
# Find all TXT files
# ------------------------------------------------------------

txt_files = sorted(HTML_FOLDER.glob("*.txt"))

if not txt_files:
    print(f"No .txt files found in: {HTML_FOLDER}")
    sys.exit(0)


print(f"Found {len(txt_files)} TXT files.")
print("-" * 60)


# ------------------------------------------------------------
# Parse each file
# ------------------------------------------------------------

success_count = 0
failed_count = 0

for txt_file in txt_files:

    # Output CSV has the same filename as the TXT file
    output_file = PARSED_FOLDER / f"{txt_file.stem}.csv"

    print(f"\nParsing:")
    print(f"  Input : {txt_file}")
    print(f"  Output: {output_file}")

    command = [
        sys.executable,
        str(PARSE_SCRIPT),
        str(txt_file),
        "-o",
        str(output_file),
    ]

    try:
        result = subprocess.run(
            command,
            check=True,
        )

        success_count += 1

    except subprocess.CalledProcessError as e:
        failed_count += 1

        print(
            f"ERROR: Failed to parse {txt_file}"
        )
        print(f"Return code: {e.returncode}")


# ------------------------------------------------------------
# Summary
# ------------------------------------------------------------

print("\n" + "=" * 60)
print("Parsing complete.")
print(f"Successful: {success_count}")
print(f"Failed:     {failed_count}")
print(f"Output folder: {PARSED_FOLDER.resolve()}")