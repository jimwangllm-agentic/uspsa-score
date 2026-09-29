# """

# Export per-stage PractiScore HTML results to a CSV file.

# The PractiScore results page embeds its match definition and fully calculated
# results as JSON in JavaScript. This parser reads those embedded values directly,
# so the combined and division rankings/percentages exactly match the page.

# python parse_practiscore_html.py html_sources\62784cac-8636-4824-ade8-4273f1096b86.html

# """

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path
from typing import Any


BASE_HEADERS = [
    "match_id",
    "match_name",
    "match_date",
    "stage_number",
    "stage_name",
    "stage_uuid",
    "shooter_name",
    "shooter_rank_combined",
    "shooter_percent_combined",
    "shooter_rank_division",
    "shooter_percent_division",
    "division",
    "class",
    "member_number",
    "power_factor",
    "categories",
    "stage_points",
    "stage_points_combined",
    "hit_factor",
    "time",
    "A",
    "B",
    "C",
    "D",
    "M",
    "NPM",
    "NS",
    "Proc",
    "Apen",
]


def extract_embedded_json(html: str, variable_name: str) -> Any:
    """Return the JSON value assigned to a JavaScript variable in the page."""
    # PractiScore first declares placeholders such as ``var matchDef = '';``.
    # Select the later assignment whose value actually begins with JSON.
    match = re.search(
        rf"\b{re.escape(variable_name)}\s*=\s*(?=[{{\[])",
        html,
    )
    if not match:
        raise RuntimeError(f"Could not find the embedded {variable_name!r} data.")

    start = match.end()
    while start < len(html) and html[start].isspace():
        start += 1

    try:
        value, _ = json.JSONDecoder().raw_decode(html[start:])
    except json.JSONDecodeError as error:
        raise RuntimeError(f"Could not decode embedded {variable_name!r} JSON.") from error

    return value


def shooter_name(shooter: dict[str, Any]) -> str:
    """Return PractiScore's display-name order: first name then last name."""
    return " ".join(
        value.strip()
        for value in (str(shooter.get("sh_fn", "")), str(shooter.get("sh_ln", "")))
        if value.strip()
    )


def categories(shooter: dict[str, Any]) -> str:
    """Flatten the optional JSON category list into a CSV-friendly string."""
    value = shooter.get("sh_ctgs", "")
    if isinstance(value, list):
        return "; ".join(map(str, value))
    if not value:
        return ""
    try:
        return "; ".join(map(str, json.loads(value)))
    except (TypeError, json.JSONDecodeError):
        return str(value)


def detail_value(details: dict[str, Any], key: str) -> str:
    """Read a score detail without treating a genuine numeric zero as missing."""
    value = details.get(key, "")
    return "" if value is None else str(value)


def parse_html(input_file: Path) -> list[dict[str, str]]:
    """Parse all per-shooter stage rows from one PractiScore HTML results file."""
    html = input_file.read_text(encoding="utf-8", errors="replace")
    match_definition = extract_embedded_json(html, "matchDef")
    results = extract_embedded_json(html, "results")

    if not isinstance(results, list) or len(results) < 2:
        raise RuntimeError("The page does not contain per-stage result data.")

    shooters = {
        shooter.get("sh_uid") or shooter.get("sh_uuid"): shooter
        for shooter in match_definition.get("match_shooters", [])
        if not shooter.get("sh_del", False)
    }
    stages = match_definition.get("match_stages", [])
    rows: list[dict[str, str]] = []

    # PractiScore places match totals at results[0], followed by one result list
    # for every match stage in the same order as match_stages.
    for stage, stage_results in zip(stages, results[1:]):
        if not isinstance(stage_results, list):
            continue

        for result in stage_results:
            shooter = shooters.get(result.get("shooterId"), {})
            details = result.get("details") or {}
            row = {
                "match_id": str(match_definition.get("match_id", input_file.stem)),
                "match_name": str(match_definition.get("match_name", "")),
                "match_date": str(match_definition.get("match_date", "")),
                "stage_number": str(stage.get("stage_number", "")),
                "stage_name": str(stage.get("stage_name", "")),
                "stage_uuid": str(stage.get("stage_uuid", "")),
                "shooter_name": shooter_name(shooter),
                "shooter_rank_combined": str(result.get("rankCombined", "")),
                "shooter_percent_combined": str(result.get("percentCombined", "")),
                "shooter_rank_division": str(result.get("rank", "")),
                "shooter_percent_division": str(result.get("percent", "")),
                "division": str(result.get("division") or shooter.get("sh_dvp", "")),
                "class": str(shooter.get("sh_grd", "")),
                "member_number": str(shooter.get("sh_id", "")),
                "power_factor": str(shooter.get("sh_pf", "")),
                "categories": categories(shooter),
                "stage_points": str(result.get("result", "")),
                "stage_points_combined": str(result.get("resultCombined", "")),
                "hit_factor": detail_value(details, "HF"),
                "time": detail_value(details, "Time"),
                "A": detail_value(details, "A"),
                "B": detail_value(details, "B"),
                "C": detail_value(details, "C"),
                "D": detail_value(details, "D"),
                "M": detail_value(details, "M"),
                "NPM": detail_value(details, "NPM"),
                "NS": detail_value(details, "NS"),
                "Proc": detail_value(details, "Proc") or detail_value(details, "P"),
                "Apen": detail_value(details, "Apen"),
            }

            # Preserve any additional format-specific details in the output.
            for key, value in details.items():
                if key not in {"HF", "Time", "A", "B", "C", "D", "M", "NPM", "NS", "Proc", "P", "Apen"}:
                    row[f"detail_{key}"] = "" if value is None else str(value)
            rows.append(row)

    if not rows:
        raise RuntimeError("No shooter stage results were found in the HTML file.")
    return rows


def output_headers(rows: list[dict[str, str]]) -> list[str]:
    """Keep stable core columns, then append any extra PractiScore details."""
    extras = sorted({key for row in rows for key in row} - set(BASE_HEADERS))
    return BASE_HEADERS + extras


def write_csv(rows: list[dict[str, str]], output_file: Path) -> None:
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with output_file.open("w", newline="", encoding="utf-8-sig") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=output_headers(rows), extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Parse PractiScore HTML stage results into a CSV file."
    )
    parser.add_argument("input", type=Path, help="PractiScore HTML results file")
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="CSV destination (defaults to parsed_stage_runnings/<HTML filename>.csv)",
    )
    args = parser.parse_args()

    if not args.input.exists():
        parser.error(f"Input file does not exist: {args.input}")
    if args.input.suffix.lower() not in {".html", ".htm"}:
        parser.error("Input must be a .html or .htm file.")

    output_file = args.output or Path("parsed_stage_runnings") / f"{args.input.stem}.csv"
    rows = parse_html(args.input)
    write_csv(rows, output_file)
    print(f"Saved {len(rows):,} shooter stage results to: {output_file}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
