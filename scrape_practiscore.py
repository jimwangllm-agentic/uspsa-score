"""Download PractiScore match result tables for a search query."""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable
from urllib.parse import parse_qs, urlencode, urljoin, urlparse, urlunparse

from bs4 import BeautifulSoup
from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError, sync_playwright


BASE_URL = "https://practiscore.com"
DEFAULT_SEARCH_URL = f"{BASE_URL}/results?query=GPS%20USPSA"
MATCH_PATH = re.compile(r"^/results/all/([0-9a-f-]+)$", re.IGNORECASE)


@dataclass
class Match:
    match_id: str
    match_name: str
    match_url: str
    date: str
    table_index: int
    columns: list[str]
    values: list[str]


class PractiScoreError(RuntimeError):
    """Raised when PractiScore cannot be crawled or parsed."""


def clean(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def set_page(url: str, page: int) -> str:
    parsed = urlparse(url)
    query = parse_qs(parsed.query, keep_blank_values=True)
    query["page"] = [str(page)]
    return urlunparse(parsed._replace(query=urlencode(query, doseq=True)))


def discover_matches(html: str, source_url: str) -> list[tuple[str, str, str]]:
    soup = BeautifulSoup(html, "html.parser")
    matches: list[tuple[str, str, str]] = []
    seen: set[str] = set()
    for anchor in soup.select("a[href]"):
        absolute_url = urljoin(source_url, anchor["href"])
        parsed = urlparse(absolute_url)
        match = MATCH_PATH.match(parsed.path)
        if not match or absolute_url in seen:
            continue
        seen.add(absolute_url)
        name = clean(anchor.get_text(" ", strip=True))
        matches.append((match.group(1), name, absolute_url))
    return matches


def parse_match(html: str, match_id: str, name: str, url: str) -> list[Match]:
    soup = BeautifulSoup(html, "html.parser")
    page_text = clean(soup.get_text(" ", strip=True))
    date_match = re.search(r"\b\d{4}-\d{2}-\d{2}\b", page_text)
    date = date_match.group(0) if date_match else ""
    rows: list[Match] = []

    tables = soup.select("table")
    if not tables:
        grids = soup.select('[role="grid"]')
        tables = []
        for grid in grids:
            header_rows = grid.select('[role="row"]:has([role="columnheader"])')
            body_rows = grid.select('[role="row"]:has([role="gridcell"])')
            if not header_rows or not body_rows:
                continue
            tables.append((header_rows[0], body_rows))

    for table_index, table in enumerate(tables):
        if isinstance(table, tuple):
            header_row, body_rows = table
            table_rows = [
                [clean(cell.get_text(" ", strip=True)) for cell in header_row.select('[role="columnheader"]')]
            ]
            table_rows.extend(
                [clean(cell.get_text(" ", strip=True)) for cell in row.select('[role="gridcell"]')]
                for row in body_rows
            )
        else:
            table_rows = []
            rows = table.select("tr")
            for row in rows:
                cells = [clean(cell.get_text(" ", strip=True)) for cell in row.select("th, td")]
                if cells:
                    table_rows.append(cells)
        if len(table_rows) < 2:
            continue

        header = table_rows[0]
        for values in table_rows[1:]:
            columns = header[:]
            if len(values) > len(columns):
                columns.extend(f"column_{index}" for index in range(len(columns), len(values)))
            values = values + [""] * (len(columns) - len(values))
            rows.append(Match(match_id, name, url, date, table_index, columns, values))
    return rows


def crawl(
    search_url: str, delay: float, timeout: float, max_pages: int, headless: bool
) -> list[Match]:
    discovered: list[tuple[str, str, str]] = []
    seen_urls: set[str] = set()

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=headless)
        page = browser.new_page()
        page.set_default_timeout(timeout * 1000)
        try:
            page.goto(set_page(search_url, 1), wait_until="domcontentloaded")
            if not headless:
                input("Complete PractiScore's verification in the browser, then press Enter here: ")

            for page_number in range(1, max_pages + 1):
                page_url = set_page(search_url, page_number)
                if page.url != page_url:
                    page.goto(page_url, wait_until="domcontentloaded")
                matches = discover_matches(page.content(), page_url)
                new_matches = [item for item in matches if item[2] not in seen_urls]
                if not new_matches:
                    break
                discovered.extend(new_matches)
                seen_urls.update(item[2] for item in new_matches)
                if page_number < max_pages:
                    time.sleep(delay)

            if not discovered:
                raise PractiScoreError(
                    "The verified browser page contained no match links. "
                    "Check the search URL or PractiScore's markup."
                )

            results: list[Match] = []
            for index, (match_id, match_name, match_url) in enumerate(discovered):
                print(f"[{index + 1}/{len(discovered)}] {match_name}", file=sys.stderr)
                page.goto(match_url, wait_until="domcontentloaded")
                results.extend(parse_match(page.content(), match_id, match_name, match_url))
                if index + 1 < len(discovered):
                    time.sleep(delay)
            return results
        except PlaywrightTimeoutError as error:
            raise PractiScoreError(f"Timed out while loading PractiScore: {error}") from error
        finally:
            browser.close()


def write_csv(rows: Iterable[Match], output: Path) -> None:
    rows = list(rows)
    all_columns: list[str] = []
    for row in rows:
        for column in row.columns:
            if column not in all_columns:
                all_columns.append(column)
    fieldnames = ["match_id", "match_name", "match_url", "date", "table_index", *all_columns]
    with output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            record = {
                "match_id": row.match_id,
                "match_name": row.match_name,
                "match_url": row.match_url,
                "date": row.date,
                "table_index": row.table_index,
            }
            record.update(dict(zip(row.columns, row.values)))
            writer.writerow(record)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", default=DEFAULT_SEARCH_URL, help="PractiScore results search URL")
    parser.add_argument("--output", type=Path, default=Path("practiscore_scores.csv"))
    parser.add_argument("--json", action="store_true", help="Write JSON instead of CSV")
    parser.add_argument("--delay", type=float, default=1.0, help="Seconds between requests")
    parser.add_argument("--timeout", type=float, default=30.0)
    parser.add_argument("--max-pages", type=int, default=50)
    parser.add_argument("--headless", action="store_true", help="Do not open a browser window")
    args = parser.parse_args()

    try:
        rows = crawl(args.url, args.delay, args.timeout, args.max_pages, args.headless)
        if args.json:
            args.output.write_text(
                json.dumps([asdict(row) for row in rows], indent=2), encoding="utf-8"
            )
        else:
            write_csv(rows, args.output)
    except PractiScoreError as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1
    print(f"Wrote {len(rows)} score rows to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())