# python collect_match_links.py "https://practiscore.com/results?query=Kidlat%20Shooters" --output match_links/Kidlat.csv

"""Collect PractiScore match-result links from one or more search pages."""

from __future__ import annotations

import argparse
import csv
import re
from pathlib import Path
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright


MATCH_PATH = re.compile(r"^/results/all/([0-9a-f-]+)$", re.IGNORECASE)


def clean(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def collect_links(html: str, source_url: str) -> list[dict[str, str]]:
    soup = BeautifulSoup(html, "html.parser")
    links: list[dict[str, str]] = []
    seen: set[str] = set()
    for anchor in soup.select("a[href]"):
        match_url = urljoin(source_url, anchor["href"])
        match_id = MATCH_PATH.match(urlparse(match_url).path)
        if not match_id or match_url in seen:
            continue
        seen.add(match_url)
        links.append(
            {
                "match_id": match_id.group(1),
                "match_name": clean(anchor.get_text(" ", strip=True)),
                "match_url": match_url,
                "source_url": source_url,
            }
        )
    return links


def write_csv(rows: list[dict[str, str]], output: Path) -> None:
    fields = ["match_id", "match_name", "match_url", "source_url"]
    with output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def open_page(playwright, cdp_url: str | None):
    if cdp_url:
        try:
            browser = playwright.chromium.connect_over_cdp(cdp_url)
        except Exception as error:
            raise RuntimeError(
                f"Could not attach to Chrome at {cdp_url}. Start Chrome with "
                "--remote-debugging-port=9222, then try again."
            ) from error
        context = browser.contexts[0] if browser.contexts else browser.new_context()
        page = context.pages[0] if context.pages else context.new_page()
        return browser, page, True
    browser = playwright.chromium.launch(headless=False)
    return browser, browser.new_page(), False


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("urls", nargs="+", help="PractiScore search URLs")
    parser.add_argument("--output", type=Path, default=Path("practiscore_match_links.csv"))
    parser.add_argument("--cdp-url", help="Attach to an existing Chrome debugging endpoint")
    args = parser.parse_args()

    all_links: list[dict[str, str]] = []
    seen: set[str] = set()
    with sync_playwright() as playwright:
        browser, page, attached = open_page(playwright, args.cdp_url)
        try:
            for url in args.urls:
                print(f"Opening {url}")
                page.goto(url, wait_until="domcontentloaded", timeout=60_000)
                input("Complete verification in the browser if shown, then press Enter here: ")
                for link in collect_links(page.content(), page.url):
                    if link["match_url"] not in seen:
                        seen.add(link["match_url"])
                        all_links.append(link)
        finally:
            if attached:
                browser.close()
            else:
                browser.close()

    write_csv(all_links, args.output)
    print(f"Wrote {len(all_links)} match links to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())