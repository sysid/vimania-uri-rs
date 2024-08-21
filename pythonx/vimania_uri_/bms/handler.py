import logging
import re
import subprocess
from typing import Tuple, Sequence

from vimania_uri_.pattern import URL_PATTERN

log = logging.getLogger("vimania-uri_.bms")


def add_twbm(url: str, current_file: str | None) -> int:
    """ Adds a bookmark using the bkmr CLI tool and allows interactive editing with vim. """
    try:
        log.info(f"Adding bookmark: {url=}, {current_file=}")
        # TODO: description should be taken from page
        result = process = subprocess.Popen(
            # ["bkmr", "add", url, "-d", current_file, "_md_", "--edit"],
            ["bkmr", "add", url, "_md_", "--edit"],
            # GOTCHA: deadlock?
            # stdout=subprocess.PIPE,
            # stderr=subprocess.PIPE,
            # text=True,
        )
        process.communicate()  # Wait for the process to complete, allowing interaction
        if process.returncode == 0:
            log.info("Bookmark added successfully.")
        else:
            log.error(f"Bookmark addition failed with return code {process.returncode}.")
        return process.returncode
    except subprocess.CalledProcessError as e:
        log.error(f"Failed to add bookmark: {e}")
        return e.returncode


def delete_twbm(line: str) -> Sequence[Tuple[int, str]]:
    """ Deletes bookmarks found in the given line using the bkmr CLI tool. """
    urls = []
    matches = re.finditer(URL_PATTERN, line)

    for match in matches:
        url = match.group()
        url = f'"{url}"'
        try:
            result = subprocess.run([
                "bkmr",
                "search",
                url,
                "--np"
            ], check=True, capture_output=True, text=True)
            id_ = result.stdout.strip()
            if id_ == "":
                log.debug(f"{url=} not found in bookmarks.")
                urls.append((0, url))
                continue

            log.debug(f"Deleting bookmark: {url=}, {id_=}")
            result = subprocess.run([
                "bkmr",
                "delete",
                id_,
            ], check=True, capture_output=True, text=True)
            urls.append((result.returncode, url))
            log.info("Bookmark deleted successfully.")
        except subprocess.CalledProcessError as e:
            log.error(f"Failed to delete bookmark: {e}")
            urls.append((e.returncode, url))
    return urls
