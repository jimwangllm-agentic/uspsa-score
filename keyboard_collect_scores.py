"""Open a PractiScore match with keyboard input and save the visible results."""

from __future__ import annotations

import argparse
import csv
import re
import time
from pathlib import Path
from urllib.parse import urlparse

import pyautogui
import pyperclip


DEFAULT_URL = (
    "https://practiscore.com/results/all/"
    "2170c5f9-ac27-4755-8693-f4d60a14c9c1"
)
MATCH_ID_PATTERN = re.compile(r"/results/all/([0-9a-f-]+)", re.IGNORECASE)
DATE_PATTERN = re.compile(r"\b\d{4}-\d{2}-\d{2}\b")


def metadata(url: str, copied_text: str) -> tuple[str, str, str]:
    match = MATCH_ID_PATTERN.search(urlparse(url).path)
    if not match:
        raise ValueError(f"Not a PractiScore match URL: {url}")
    match_id = match.group(1)
    lines = [line.strip() for line in copied_text.splitlines() if line.strip()]
    match_date = next((item for item in lines if DATE_PATTERN.fullmatch(item)), "")
    if not match_date:
        found_date = DATE_PATTERN.search(copied_text)
        match_date = found_date.group(0) if found_date else ""
    match_name = next(
        (line for line in lines if "USPSA" in line and not DATE_PATTERN.search(line)),
        match_id,
    )
    return match_id, match_name, match_date


def write_csv(url: str, copied_text: str, output: Path) -> None:
    match_id, match_name, match_date = metadata(url, copied_text)
    rows = [[line] for line in copied_text.splitlines() if line.strip()]
    with output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["match_id", "match_name", "match_date", "source_url", "copied_score_text"])
        for row in rows:
            writer.writerow([match_id, match_name, match_date, url, row[0]])


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("url", nargs="?", default=DEFAULT_URL)
    parser.add_argument("--wait", type=float, default=10.0)
    parser.add_argument("--output-dir", type=Path, default=Path("match_scores"))
    args = parser.parse_args()

    print("1. Opening Windows search")
    pyautogui.press("win")
    time.sleep(1)
    print("2. Opening Chrome")
    pyautogui.write("chrome", interval=0.05)
    pyautogui.press("enter")
    time.sleep(3)
    print("3. Bringing Chrome to the foreground")
    pyautogui.hotkey("alt", "tab")
    time.sleep(1)
    print("4. Moving focus with Tab")
    pyautogui.press("tab")
    time.sleep(1)
    print("5. Focusing the address bar and entering the URL")
    pyautogui.hotkey("ctrl", "l")
    pyautogui.write(args.url, interval=0.002)
    pyautogui.press("enter")
    print(f"6. Waiting {args.wait:g} seconds for the page and verification")
    time.sleep(args.wait)
    print("7. Copying visible score data")
    pyautogui.hotkey("ctrl", "a")
    pyautogui.hotkey("ctrl", "c")
    time.sleep(1)
    copied_text = pyperclip.paste()
    if not copied_text.strip():
        raise RuntimeError("Chrome copied no visible page data")

    match = MATCH_ID_PATTERN.search(urlparse(args.url).path)
    if not match:
        raise ValueError(f"Not a PractiScore match URL: {args.url}")
    output = args.output_dir / f"{match.group(1)}.csv"
    args.output_dir.mkdir(parents=True, exist_ok=True)
    write_csv(args.url, copied_text, output)
    print(f"8. Wrote copied score data to {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())