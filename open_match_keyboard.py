"""Open a PractiScore match in Chrome and move to the account choice."""

from __future__ import annotations

import argparse
import time

import pyautogui


DEFAULT_URL = (
    "https://practiscore.com/results/all/"
    "2170c5f9-ac27-4755-8693-f4d60a14c9c1"
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("url", nargs="?", default=DEFAULT_URL)
    parser.add_argument("--load-wait", type=float, default=5.0)
    args = parser.parse_args()

    time.sleep(1)
    pyautogui.hotkey("alt", "tab")
    time.sleep(1)
    pyautogui.hotkey("ctrl", "l")
    pyautogui.write(args.url, interval=0.002)
    pyautogui.press("enter")
    time.sleep(args.load_wait)
    pyautogui.press("tab")
    print("Pressed Tab; the next account choice should now be focused.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())