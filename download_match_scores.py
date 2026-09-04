# cd "C:\Users\pcc20\test\uspsa-score"
# python download_match_scores.py "https://practiscore.com/results/all/7ab5f726-bc21-4b6d-a802-8e5f6baf7a9f"


"""
Open a URL in Microsoft Edge and save both:

1. The original webpage's copied/rendered text to a .txt file.
2. The original HTML source code to a .html file.

The webpage text is copied FIRST, followed by the HTML source.

Both filenames are based on the SHA-256 hash of the input URL.

At the end, both the source tab and the original webpage tab are closed.
"""

from __future__ import annotations

import argparse
import hashlib
import time
from pathlib import Path
from urllib.parse import urlparse

import pyautogui
import pyperclip


def output_paths(url: str, output_dir: Path) -> tuple[Path, Path]:
    """Return TXT and HTML filenames based on the URL's SHA-256 hash."""
    url_hash = hashlib.sha256(url.encode("utf-8")).hexdigest()

    txt_path = output_dir / f"{url_hash}.txt"
    html_path = output_dir / f"{url_hash}.html"

    return txt_path, html_path


def copy_page_text() -> str:
    """Copy the original webpage's rendered text."""
    # Make sure the webpage has focus.
    pyautogui.click()
    time.sleep(0.3)

    # Clear the clipboard first.
    pyperclip.copy("")

    # Select all webpage text.
    pyautogui.hotkey("ctrl", "a")
    time.sleep(0.5)

    # Copy selected text.
    pyautogui.hotkey("ctrl", "c")
    time.sleep(1)

    return pyperclip.paste()


def copy_source_code() -> str:
    """Open Edge's View Source tab and copy the HTML source."""
    pyautogui.hotkey("ctrl", "u")
    time.sleep(2)

    # Clear the clipboard first.
    pyperclip.copy("")

    # Select all source code.
    pyautogui.hotkey("ctrl", "a")
    time.sleep(0.5)

    # Copy source code.
    pyautogui.hotkey("ctrl", "c")
    time.sleep(1)

    return pyperclip.paste()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument(
        "url",
        help="The http:// or https:// URL to save."
    )

    parser.add_argument(
        "--wait",
        type=float,
        default=10.0,
        help="Page-load wait in seconds."
    )

    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("html_sources")
    )

    args = parser.parse_args()

    # ---------------------------------------------------------
    # Validate URL
    # ---------------------------------------------------------

    parsed_url = urlparse(args.url)

    if parsed_url.scheme not in {"http", "https"} or not parsed_url.netloc:
        parser.error(
            "url must be a complete http:// or https:// URL"
        )

    if args.wait < 0:
        parser.error("--wait must be zero or greater")

    # ---------------------------------------------------------
    # Open Microsoft Edge
    # ---------------------------------------------------------

    print("1. Opening Microsoft Edge")

    pyautogui.press("win")
    time.sleep(1)

    pyautogui.write("edge", interval=0.05)
    pyautogui.press("enter")
    time.sleep(3)

    # ---------------------------------------------------------
    # Enter URL
    # ---------------------------------------------------------

    print("2. Entering the URL in Edge's address bar")

    pyautogui.hotkey("ctrl", "l")
    pyautogui.write(args.url, interval=0.002)
    pyautogui.press("enter")

    # ---------------------------------------------------------
    # Wait for page
    # ---------------------------------------------------------

    print(
        f"3. Waiting {args.wait:g} seconds for the page to load"
    )

    time.sleep(args.wait)

    # ---------------------------------------------------------
    # FIRST: Copy original webpage text
    # ---------------------------------------------------------

    print(
        "4. Copying the original webpage text"
    )

    page_text = copy_page_text()

    if not page_text.strip():
        raise RuntimeError(
            "Edge copied no webpage text; the TXT file was not created."
        )

    print(
        f"   Copied {len(page_text):,} characters of webpage text"
    )

    # ---------------------------------------------------------
    # SECOND: Open View Source and copy HTML
    # ---------------------------------------------------------

    print(
        "5. Opening and copying the original HTML source"
    )

    source_code = copy_source_code()

    if not source_code.strip():
        # Close the source tab before raising the error.
        pyautogui.hotkey("ctrl", "w")

        raise RuntimeError(
            "Edge copied no source code; the HTML file was not created."
        )

    print(
        f"   Copied {len(source_code):,} characters of HTML source"
    )

    # ---------------------------------------------------------
    # Create output directory
    # ---------------------------------------------------------

    args.output_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    # ---------------------------------------------------------
    # Generate filenames
    # ---------------------------------------------------------

    txt_path, html_path = output_paths(
        args.url,
        args.output_dir
    )

    # ---------------------------------------------------------
    # Save webpage text FIRST
    # ---------------------------------------------------------

    txt_path.write_text(
        page_text,
        encoding="utf-8"
    )

    print(f"6. Saved webpage text to {txt_path}")

    # ---------------------------------------------------------
    # Save HTML source SECOND
    # ---------------------------------------------------------

    html_path.write_text(
        source_code,
        encoding="utf-8"
    )

    print(f"7. Saved HTML source to {html_path}")

    # ---------------------------------------------------------
    # Close source tab
    # ---------------------------------------------------------

    print("8. Closing the View Source tab")

    pyautogui.hotkey("ctrl", "w")
    time.sleep(1)

    # ---------------------------------------------------------
    # Close original webpage
    # ---------------------------------------------------------

    print("9. Closing the original webpage")

    pyautogui.hotkey("ctrl", "w")
    time.sleep(1)

    print("10. Finished")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
