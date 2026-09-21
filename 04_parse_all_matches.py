# cd "C:\Users\pcc20\test\uspsa-score"
#
# python 04_parse_all_matches.py

import subprocess
import logging
from pathlib import Path


# ------------------------------------------------------------
# Configuration
# ------------------------------------------------------------

HTML_FOLDER = Path("html_sources")
PARSED_FOLDER = Path("parsed")

PARSE_SCRIPT = "parse_practiscore.py"


# ------------------------------------------------------------
# Logging
# ------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger(__name__)


# ------------------------------------------------------------
# Create output folder
# ------------------------------------------------------------

PARSED_FOLDER.mkdir(exist_ok=True)


# ------------------------------------------------------------
# Find TXT files
# ------------------------------------------------------------

txt_files = sorted(HTML_FOLDER.glob("*.txt"))


# ------------------------------------------------------------
# Process TXT files
# ------------------------------------------------------------

for txt_file in txt_files:

    match_id = txt_file.stem

    parsed_file = PARSED_FOLDER / f"{match_id}.csv"


    # --------------------------------------------------------
    # Skip if CSV already exists
    # --------------------------------------------------------

    if (
        parsed_file.exists()
        and parsed_file.stat().st_size > 0
    ):
        continue


    # --------------------------------------------------------
    # Skip empty TXT
    # --------------------------------------------------------

    if (
        not txt_file.exists()
        or txt_file.stat().st_size == 0
    ):

        logger.warning(
            "EMPTY | %s",
            txt_file.name
        )

        continue


    # --------------------------------------------------------
    # Process
    # --------------------------------------------------------

    logger.info(
        "PROCESS | %s",
        txt_file.name
    )


    try:

        result = subprocess.run(
            [
                "python",
                PARSE_SCRIPT,
                str(txt_file),
                "-o",
                str(parsed_file)
            ],
            check=False
        )


    except Exception as e:

        logger.error(
            "ERROR | %s | %s",
            txt_file.name,
            e
        )

        continue


    # --------------------------------------------------------
    # Parser failed
    # --------------------------------------------------------

    if result.returncode != 0:

        logger.error(
            "FAILED | %s | parser exit code %s",
            txt_file.name,
            result.returncode
        )

        continue


    # --------------------------------------------------------
    # Verify output
    # --------------------------------------------------------

    if (
        parsed_file.exists()
        and parsed_file.stat().st_size > 0
    ):

        logger.info(
            "SUCCESS | %s -> %s",
            txt_file.name,
            parsed_file.name
        )

    else:

        logger.error(
            "FAILED | %s | CSV was not created",
            txt_file.name
        )


# ------------------------------------------------------------
# Finished
# ------------------------------------------------------------

logger.info(
    "DONE | %d TXT files scanned",
    len(txt_files)
)