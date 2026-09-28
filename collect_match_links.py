# Example:
# python collect_match_links.py "https://practiscore.com/results?query=brazosland%20uspsa" --output match_links/Brazosland.csv


"""
Open PractiScore search pages in Microsoft Edge, save the rendered HTML,
and collect match-result links from the saved HTML.
"""

from __future__ import annotations

import argparse
import csv
import re
import time
from pathlib import Path
from urllib.parse import urlparse

import pyautogui
from bs4 import BeautifulSoup


MATCH_PATH = re.compile(
    r"^/results/all/([0-9a-f-]+)$",
    re.IGNORECASE,
)


def clean(value: str) -> str:
    """Normalize whitespace."""
    return re.sub(r"\s+", " ", value).strip()


def safe_filename(url: str) -> str:
    """
    Create a filesystem-safe filename from a URL.
    """

    parsed = urlparse(url)

    if parsed.query:
        name = parsed.query
    else:
        name = parsed.path.strip("/")

    name = re.sub(
        r"[^A-Za-z0-9._-]+",
        "_",
        name,
    )

    if not name:
        name = "page"

    return name[:150]


def open_edge(
    url: str,
    wait: float,
) -> None:
    """
    Open Microsoft Edge and navigate to the supplied URL.
    """

    print("1. Opening Microsoft Edge")

    pyautogui.press("win")
    time.sleep(1)

    pyautogui.write(
        "edge",
        interval=0.05,
    )

    time.sleep(0.5)

    pyautogui.press("enter")

    # Give Edge time to start.
    time.sleep(2)

    # ---------------------------------------------------------
    # Enter URL
    # ---------------------------------------------------------

    print("2. Entering the URL in Edge's address bar")

    pyautogui.hotkey(
        "ctrl",
        "l",
    )

    pyautogui.write(
        url,
        interval=0.002,
    )

    pyautogui.press("enter")

    # ---------------------------------------------------------
    # Wait for page
    # ---------------------------------------------------------

    print(
        f"3. Waiting {wait:g} seconds for the page to load"
    )

    time.sleep(wait)


def save_current_page(
    output_file: Path,
) -> Path:
    """
    Save the currently displayed Edge page using Ctrl+S.

    Returns the actual HTML file created by Edge.
    """

    print(
        f"4. Saving current page to {output_file}"
    )

    output_file.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    # ---------------------------------------------------------
    # Remove stale files from previous runs
    # ---------------------------------------------------------

    possible_files = [
        output_file,
        output_file.with_suffix(".htm"),
        output_file.with_suffix(".html"),
    ]

    for file in possible_files:
        try:
            if file.exists():
                file.unlink()
        except OSError:
            pass

    # ---------------------------------------------------------
    # Open Save As
    # ---------------------------------------------------------

    pyautogui.hotkey(
        "ctrl",
        "s",
    )

    time.sleep(2)

    # ---------------------------------------------------------
    # Enter complete path
    # ---------------------------------------------------------

    pyautogui.hotkey(
        "ctrl",
        "a",
    )

    time.sleep(0.2)

    pyautogui.write(
        str(output_file.resolve()),
        interval=0.002,
    )

    pyautogui.press("enter")

    # ---------------------------------------------------------
    # Wait for Edge to finish saving
    # ---------------------------------------------------------

    print(
        "   Waiting for Edge to finish saving..."
    )

    for _ in range(30):

        time.sleep(0.5)

        # Exact filename
        if output_file.exists():

            print(
                f"   Saved: {output_file}"
            )

            return output_file

        # Edge may change .html to .htm
        htm_file = output_file.with_suffix(
            ".htm"
        )

        if htm_file.exists():

            print(
                f"   Saved: {htm_file}"
            )

            return htm_file

        # Edge may append/change extension
        html_file = output_file.with_suffix(
            ".html"
        )

        if html_file.exists():

            print(
                f"   Saved: {html_file}"
            )

            return html_file

    # ---------------------------------------------------------
    # Look for recently created HTML files
    # ---------------------------------------------------------

    candidates = []

    for pattern in (
        "*.html",
        "*.htm",
    ):

        candidates.extend(
            output_file.parent.glob(pattern)
        )

    if candidates:

        candidates.sort(
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )

        newest = candidates[0]

        print(
            "   Exact filename was not found."
        )

        print(
            f"   Using newest HTML file: {newest}"
        )

        return newest

    # ---------------------------------------------------------
    # Nothing found
    # ---------------------------------------------------------

    print()
    print(
        "ERROR: Edge did not create an HTML file."
    )

    print(
        f"Expected directory:"
        f" {output_file.parent.resolve()}"
    )

    print()
    print(
        "Files currently in the directory:"
    )

    try:

        for file in output_file.parent.iterdir():
            print(
                f"   {file.name}"
            )

    except OSError as error:

        print(
            f"   Could not list directory: {error}"
        )

    raise FileNotFoundError(
        f"Could not find saved HTML for "
        f"{output_file}"
    )


def parse_match_links(
    html_file: Path,
    source_url: str,
) -> list[dict[str, str]]:
    """
    Parse PractiScore match information from a saved HTML page.

    Expected structure:

        <div class="ais-hits--item">
            <li class="search-result-list-item ...">

                <div class="search-result-list-details ...">

                    <h5 class="search-result-list-title ...">

                        <a href="https://practiscore.com/results/all/...">

                            <span class="ais-highlight">
                                ...
                            </span>

                        </a>

                        <small>
                            • updated 2 years ago
                        </small>

                    </h5>

                    <p class="search-result-list-subtitle">

                        <span>2024-10-13</span>
                        •
                        <span>USPSA</span>

                    </p>

                </div>

            </li>
        </div>
    """

    print(
        f"5. Reading saved HTML: {html_file}"
    )

    if not html_file.exists():

        raise FileNotFoundError(
            f"HTML file does not exist: "
            f"{html_file}"
        )

    html = html_file.read_text(
        encoding="utf-8",
        errors="replace",
    )

    soup = BeautifulSoup(
        html,
        "html.parser",
    )

    links: list[dict[str, str]] = []

    seen: set[str] = set()

    # ---------------------------------------------------------
    # Find PractiScore search-result items
    # ---------------------------------------------------------

    items = soup.select(
        "div.ais-hits--item"
    )

    print(
        f"   Found {len(items)} search-result items"
    )

    # ---------------------------------------------------------
    # Parse each result
    # ---------------------------------------------------------

    for item in items:

        # -----------------------------------------------------
        # Match link
        # -----------------------------------------------------

        anchor = item.select_one(
            "h5.search-result-list-title a[href]"
        )

        if not anchor:
            continue

        match_url = anchor.get(
            "href",
            "",
        ).strip()

        parsed_url = urlparse(
            match_url
        )

        match = MATCH_PATH.match(
            parsed_url.path
        )

        if not match:
            continue

        match_id = match.group(1)

        # -----------------------------------------------------
        # Deduplicate
        # -----------------------------------------------------

        if match_url in seen:
            continue

        seen.add(match_url)

        # -----------------------------------------------------
        # Match name
        # -----------------------------------------------------

        title_element = item.select_one(
            "h5.search-result-list-title"
        )

        if title_element:

            # Remove:
            #
            # <small> • updated 2 years ago </small>
            #
            small = title_element.select_one(
                "small"
            )

            if small:
                small.extract()

            match_name = clean(
                title_element.get_text(
                    " ",
                    strip=True,
                )
            )

        else:

            match_name = clean(
                anchor.get_text(
                    " ",
                    strip=True,
                )
            )

        # -----------------------------------------------------
        # Date and match type
        # -----------------------------------------------------

        match_date = ""
        match_type = ""

        subtitle = item.select_one(
            "p.search-result-list-subtitle"
        )

        if subtitle:

            spans = subtitle.select(
                "span"
            )

            values = [
                clean(
                    span.get_text(
                        " ",
                        strip=True,
                    )
                )
                for span in spans
            ]

            if len(values) >= 1:
                match_date = values[0]

            if len(values) >= 2:
                match_type = values[1]

        # -----------------------------------------------------
        # Add result
        # -----------------------------------------------------

        links.append(
            {
                "match_id": match_id,
                "match_name": match_name,
                "match_url": match_url,
                "match_date": match_date,
                "match_type": match_type,
                "source_url": source_url,
            }
        )

    return links


def write_csv(
    rows: list[dict[str, str]],
    output: Path,
) -> None:
    """
    Write collected match information to CSV.
    """

    output.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    fields = [
        "match_id",
        "match_name",
        "match_url",
        "match_date",
        "match_type",
        "source_url",
    ]

    with output.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as handle:

        writer = csv.DictWriter(
            handle,
            fieldnames=fields,
        )

        writer.writeheader()

        writer.writerows(rows)


def main() -> int:

    parser = argparse.ArgumentParser(
        description=__doc__
    )

    parser.add_argument(
        "urls",
        nargs="+",
        help="PractiScore search URLs",
    )

    parser.add_argument(
        "--output",
        type=Path,
        default=Path(
            "practiscore_match_links.csv"
        ),
    )

    parser.add_argument(
        "--wait",
        type=float,
        default=8,
        help=(
            "Seconds to wait after opening "
            "each page. Default: 8"
        ),
    )

    parser.add_argument(
        "--pages-dir",
        type=Path,
        default=Path(
            "match_link_pages"
        ),
        help=(
            "Directory where saved HTML pages "
            "are stored."
        ),
    )

    args = parser.parse_args()

    # ---------------------------------------------------------
    # Combined results
    # ---------------------------------------------------------

    all_links: list[
        dict[str, str]
    ] = []

    seen: set[str] = set()

    args.pages_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    # ---------------------------------------------------------
    # Process each search URL
    # ---------------------------------------------------------

    for index, url in enumerate(
        args.urls,
        start=1,
    ):

        print()
        print("=" * 70)
        print(
            f"Processing page "
            f"{index}/{len(args.urls)}"
        )
        print("=" * 70)

        # -----------------------------------------------------
        # Open Edge
        # -----------------------------------------------------

        open_edge(
            url,
            args.wait,
        )

        # -----------------------------------------------------
        # Determine saved filename
        # -----------------------------------------------------

        filename = (
            f"{index:03d}_"
            f"{safe_filename(url)}.html"
        )

        html_file = (
            args.pages_dir / filename
        )

        # -----------------------------------------------------
        # Save current Edge page
        # -----------------------------------------------------

        actual_html_file = (
            save_current_page(
                html_file
            )
        )

        # -----------------------------------------------------
        # Parse saved HTML
        # -----------------------------------------------------

        links = parse_match_links(
            actual_html_file,
            url,
        )

        print(
            f"6. Parsed {len(links)} match links"
        )

        # -----------------------------------------------------
        # Combine and deduplicate
        # -----------------------------------------------------

        for link in links:

            match_url = link[
                "match_url"
            ]

            if match_url in seen:
                continue

            seen.add(match_url)

            all_links.append(link)

    # ---------------------------------------------------------
    # Write CSV
    # ---------------------------------------------------------

    print()
    print("=" * 70)
    print(
        f"7. Writing "
        f"{len(all_links)} matches"
    )
    print("=" * 70)

    write_csv(
        all_links,
        args.output,
    )

    print()
    print(
        f"Done. Wrote "
        f"{len(all_links)} match links "
        f"to {args.output}"
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(
        main()
    )