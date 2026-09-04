# cd "C:\Users\pcc20\test\uspsa-score"
# python parse_practiscore.py html_sources/3fff1f16a854cb9102009f5695d7b4ea2773c0fe51694f41b53397b10d8d5ba1.txt -o parsed/3fff1f16a854cb9102009f5695d7b4ea2773c0fe51694f41b53397b10d8d5ba1.csv

from __future__ import annotations

import argparse
import csv
import re
from pathlib import Path


HEADERS = [
    "Name",
    "%",
    "Pts",
    "Time",
    "% psbl",
    "Div",
    "Class",
    "Cats",
    "PF",
    "Mem #",
    "A",
    "C",
    "D",
    "M",
    "NPM",
    "NS",
    "Proc",
    "Apen",
]

OUTPUT_HEADERS = [
    "match_id",
    "match_name",
    "match_date",
    "rank",
    "Name",
    "%",
    "Pts",
    "Time",
    "% psbl",
    "Div",
    "Class",
    "Cats",
    "PF",
    "Mem #",
    "A",
    "C",
    "D",
    "M",
    "NPM",
    "NS",
    "Proc",
    "Apen",
]


def parse_match_info(lines: list[str]) -> tuple[str, str, str]:
    """
    Extract match ID, match name, and match date from PractiScore TXT.

    Example source:

        GPS USPSA February Extra Saturday 2026 USPSA 2026-02-28Generation P C

    Expected result:

        match_name = GPS USPSA February Extra Saturday 2026
        match_date = 2026-02-28
    """

    match_id = ""
    match_name = ""
    match_date = ""

    for line in lines:
        line = line.strip()

        if not line:
            continue

        # Look for YYYY-MM-DD anywhere in the line.
        date_match = re.search(
            r"(\d{4}-\d{2}-\d{2})",
            line,
        )

        if not date_match:
            continue

        match_date = date_match.group(1)

        # Everything before the date.
        before_date = line[:date_match.start()].strip()

        # Remove trailing organization name.
        #
        # Example:
        #
        # GPS USPSA February Extra Saturday 2026 USPSA
        #                                             ^^^^^
        #
        before_date = re.sub(
            r"\s+USPSA\s*$",
            "",
            before_date,
            flags=re.IGNORECASE,
        ).strip()

        match_name = before_date

        # Debug output so we can see exactly what was extracted.
        print(f"DEBUG source line: {line!r}")
        print(f"DEBUG before date:  {before_date!r}")
        print(f"DEBUG match name:   {match_name!r}")
        print(f"DEBUG match date:   {match_date!r}")

        break

    # Try to find an explicit match ID anywhere in the text.
    id_patterns = [
        r"\bmatch[_ ]?id\s*[:#]?\s*([A-Za-z0-9_-]+)",
        r"\bid\s*[:#]\s*(\d+)",
        r"\bmatchid\s*[:#]?\s*([A-Za-z0-9_-]+)",
    ]

    full_text = "\n".join(lines)

    for pattern in id_patterns:
        match = re.search(
            pattern,
            full_text,
            re.IGNORECASE,
        )

        if match:
            match_id = match.group(1)
            break

    return match_id, match_name, match_date


def parse_rank_and_name(value: str) -> tuple[str, str]:
    """
    Convert:

        1-Gil Yolo

    into:

        rank = 1
        Name = Gil Yolo
    """

    match = re.match(r"^\s*(\d+)\s*-\s*(.*)$", value)

    if match:
        return match.group(1), match.group(2).strip()

    return "", value.strip()


def find_results_header(lines: list[str]) -> int:
    """Find the actual PractiScore results header."""

    normalized_target = "\t".join(HEADERS)

    for i, line in enumerate(lines):
        if line.strip() == normalized_target:
            return i

    raise RuntimeError(
        "Could not find the PractiScore results header."
    )


def parse_results(
    lines: list[str],
    header_index: int,
    match_id: str,
    match_name: str,
    match_date: str,
) -> list[dict[str, str]]:

    rows: list[dict[str, str]] = []

    # Data starts immediately after the header.
    for line in lines[header_index + 1:]:

        # Stop once we reach the repeated "Name" section,
        # "Old style results", "Classifier Report", etc.
        stripped = line.strip()

        if stripped in {
            "",
            "Name",
            "Old style results",
            "Classifier Report for USPSA",
            "Score Edit History",
        }:
            continue

        # A results row has tab-separated columns.
        parts = line.split("\t")

        # We only want actual competitor rows.
        if len(parts) != len(HEADERS):
            continue

        # The first field should start with a ranking number.
        if not re.match(r"^\s*\d+\s*-", parts[0]):
            continue

        rank, name = parse_rank_and_name(parts[0])

        row = {
            "match_id": match_id,
            "match_name": match_name,
            "match_date": match_date,
            "rank": rank,
        }

        # Add the remaining PractiScore fields.
        for header, value in zip(HEADERS[1:], parts[1:]):
            row[header] = value.strip()

        # Replace the original "Name" field with the cleaned name.
        row["Name"] = name

        rows.append(row)

    return rows


def parse_file(input_file: Path, output_file: Path) -> None:
    """Parse one PractiScore TXT file into CSV."""

    text = input_file.read_text(
        encoding="utf-8",
        errors="replace",
    )

    lines = text.splitlines()

    # ---------------------------------------------------------
    # Match information
    # ---------------------------------------------------------

    match_id, match_name, match_date = parse_match_info(lines)

    print(f"Match ID:   {match_id or '(not found)'}")
    print(f"Match name: {match_name}")
    print(f"Match date: {match_date}")

    # ---------------------------------------------------------
    # Find results table
    # ---------------------------------------------------------

    header_index = find_results_header(lines)

    print(
        f"Results header found on line {header_index + 1}"
    )

    # ---------------------------------------------------------
    # Parse competitors
    # ---------------------------------------------------------

    rows = parse_results(
        lines,
        header_index,
        match_id,
        match_name,
        match_date,
    )

    if not rows:
        raise RuntimeError(
            "No competitor rows were found."
        )

    # ---------------------------------------------------------
    # Write CSV
    # ---------------------------------------------------------

    output_file.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with output_file.open(
        "w",
        newline="",
        encoding="utf-8-sig",
    ) as f:

        writer = csv.DictWriter(
            f,
            fieldnames=OUTPUT_HEADERS,
            extrasaction="ignore",
        )

        writer.writeheader()
        writer.writerows(rows)

    print(f"Saved {len(rows)} competitors to:")
    print(output_file)


def main() -> int:

    parser = argparse.ArgumentParser(
        description=(
            "Parse a PractiScore TXT export into CSV."
        )
    )

    parser.add_argument(
        "input",
        type=Path,
        help="PractiScore TXT file",
    )

    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="Output CSV file",
    )

    args = parser.parse_args()

    if not args.input.exists():
        parser.error(
            f"Input file does not exist: {args.input}"
        )

    # If no output filename is supplied, automatically
    # replace .txt with .csv.
    output_file = args.output

    if output_file is None:
        output_file = args.input.with_suffix(".csv")

    parse_file(
        args.input,
        output_file,
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())