"""Batch-export all PractiScore HTML stage results to CSV files.

Each HTML file in ``html_sources`` is processed by ``parse_practiscore_html``.
Its CSV is written to ``parsed_stage_runnings`` using the same filename stem.

python 05_parse_all_stages.py

"""

from __future__ import annotations

import argparse
import logging
from pathlib import Path

from parse_practiscore_html import parse_html, write_csv


DEFAULT_HTML_FOLDER = Path("html_sources")
DEFAULT_OUTPUT_FOLDER = Path("parsed_stage_runnings")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Parse every PractiScore HTML results file into per-stage CSV files."
    )
    parser.add_argument(
        "--input-dir",
        type=Path,
        default=DEFAULT_HTML_FOLDER,
        help=f"Folder containing .html files (default: {DEFAULT_HTML_FOLDER})",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_FOLDER,
        help=f"Folder for per-match CSV files (default: {DEFAULT_OUTPUT_FOLDER})",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Recreate CSV files that already exist.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
    )
    logger = logging.getLogger(__name__)

    if not args.input_dir.is_dir():
        logger.error("Input folder does not exist: %s", args.input_dir)
        return 1

    args.output_dir.mkdir(parents=True, exist_ok=True)
    html_files = sorted(
        path
        for pattern in ("*.html", "*.htm")
        for path in args.input_dir.glob(pattern)
    )

    if not html_files:
        logger.warning("No HTML files found in: %s", args.input_dir)
        return 0

    processed = skipped = failed = total_rows = 0

    for html_file in html_files:
        output_file = args.output_dir / f"{html_file.stem}.csv"

        if not args.force and output_file.exists() and output_file.stat().st_size > 0:
            logger.info("SKIP    | %s | output already exists", html_file.name)
            skipped += 1
            continue

        if html_file.stat().st_size == 0:
            logger.warning("SKIP    | %s | source file is empty", html_file.name)
            skipped += 1
            continue

        logger.info("PROCESS | %s", html_file.name)
        try:
            rows = parse_html(html_file)
            write_csv(rows, output_file)
        except (OSError, RuntimeError, ValueError) as error:
            logger.error("FAILED  | %s | %s", html_file.name, error)
            failed += 1
            continue

        processed += 1
        total_rows += len(rows)
        logger.info("SUCCESS | %s -> %s | %s rows", html_file.name, output_file.name, len(rows))

    logger.info(
        "DONE | %s HTML files scanned | %s processed | %s skipped | %s failed | %s stage rows",
        len(html_files),
        processed,
        skipped,
        failed,
        total_rows,
    )
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
