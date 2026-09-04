# uspsa-score

Crawler for the public PractiScore search results matching `GPS USPSA`.

## Step 1: Collect Match Links

Run the link collector with one or more PractiScore search URLs:

```powershell
py collect_match_links.py "https://practiscore.com/results?query=GPS%20USPSA"
```

The script opens a browser and loads each URL. Complete any PractiScore
verification in the browser, return to the terminal, and press Enter. It then
collects every match-result link from the page and saves them to
`practiscore_match_links.csv`.

Multiple URLs can be supplied in one command:

```powershell
py collect_match_links.py "https://practiscore.com/results?query=GPS%20USPSA" "https://practiscore.com/results?query=USPSA"
```

To reuse an already verified Chrome profile instead of launching a new browser,
start Chrome with remote debugging enabled and attach to it:

```powershell
chrome.exe --remote-debugging-port=9222
py collect_match_links.py --cdp-url http://127.0.0.1:9222 "https://practiscore.com/results?query=GPS%20USPSA"
```

The same option works for Step 2:

```powershell
py download_match_scores.py --cdp-url http://127.0.0.1:9222 --links-csv practiscore_match_links.csv
```

Chrome must be started with remote debugging before the script can attach. A
normal Chrome window does not expose its active profile to another process.

## Open A Match With Keyboard Input

To open the selected match and press `Tab` after the page loads:

```powershell
py open_match_keyboard.py
```

Make Chrome the active window when the script asks, then press Enter in the
terminal. The script uses `Ctrl+L`, types the URL, presses Enter, waits five
seconds, and presses Tab to focus the next account choice.

For the complete keyboard-only workflow, including copying the visible page
data and saving it to a match-ID CSV:

```powershell
py keyboard_collect_scores.py
```

This performs: Windows key, type `Microsoft Edge`, Enter, Tab, focus the address bar,
type the URL, Enter, wait 10 seconds, copy the visible page, and save the
result under `match_scores`.

## Step 2: Download Match Scores

Download one match directly:

```powershell
py download_match_scores.py "https://practiscore.com/results/all/bff00c64-dc88-41dc-83b4-6085e754cd7e"
```

For every match page, the script waits five seconds before reading the page,
then pauses for browser verification if it is shown. Each result is saved under
`match_scores` using the match ID as the filename, for example
`match_scores/bff00c64-dc88-41dc-83b4-6085e754cd7e.csv`. The CSV includes
`match_id` and `match_name` columns before the score columns.

To download every match collected in Step 1:

```powershell
py download_match_scores.py --links-csv practiscore_match_links.csv
```

## Setup

```powershell
py -m pip install -r requirements.txt
py -m playwright install chromium
```

## Run

```powershell
py scrape_practiscore.py
```

The default command opens a visible Chromium window. Complete PractiScore's
verification there, return to the terminal, and press Enter. The crawler then
uses that same verified browser session to discover match links, download score
grids, and write `practiscore_scores.csv`. Use `--json` and a `.json` output
path for one record per score row:

```powershell
py scrape_practiscore.py --json --output practiscore_scores.json --delay 2
```

You can provide another PractiScore search URL with `--url`, or use
`--headless` after a browser profile has already been verified. Keep the request
delay respectful of the site's terms and capacity.



python download_match_scores.py 'https://practiscore.com/results/all/8d8d093e-8f97-4253-9069-1b454f8808c6'

python download_match_scores.py 'https://practiscore.com/results/all/6876bc8c-98c9-4785-a901-3132faee1b3c'