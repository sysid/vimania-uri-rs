from __future__ import print_function

import logging
import os.path
import re
import subprocess
import sys
import webbrowser
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, NewType, Optional, Tuple

from vimania_uri_.pattern import (
    URL_PATTERN,
    MD_LINK_PATTERN,
    LINK_PATTERN,
    REFERENCE_DEFINITION_PATTERN,
)

try:
    from urllib.parse import urlparse
except ImportError:
    # noinspection PyUnresolvedReferences
    from urlparse import urlparse

_log = logging.getLogger("vimania-uri_.md.mdnav")

URI = NewType("URI", str)


@dataclass
class ParsedPath(object):
    path: str
    line: int = None
    anchor: str = None
    scheme: str = None

    @property
    def fullpath(self) -> str:
        if self.path is None or self.path == "":
            return ""
        if self.scheme is not None:
            return self.path
        return str(Path(os.path.expandvars(self.path)).expanduser().absolute())


def parse_uri(uri: URI) -> ParsedPath:
    """Parse a uri with optional line number of anchor into its parts.

    For example::

        parse_path('foo.md:30') == ParsedPath('foo.md', line=30)
        parse_path('foo.md#anchor') == ParsedPath('foo.md', anchor='anchor')

    """
    line, anchor, ext = None, None, None
    if uri is None:
        return ParsedPath(path="")
    if has_scheme(uri):
        scheme, netloc, p, params, query, fragment = urlparse(uri)
        return ParsedPath(scheme=scheme, path=uri)

    p = Path(uri)
    path = p.stem
    ext = p.suffix
    if "#" in p.suffix:
        ext, anchor = p.suffix.rsplit("#", 1)

    elif ":" in p.suffix:
        ext, line = p.suffix.rsplit(":", 1)

    path = f"{p.parent}/{path}{ext}"
    return ParsedPath(
        path=path,
        line=line,
        anchor=anchor,
    )


def open_uri(
    target: URI,
    open_in_vim_extensions: set = None,
    current_file: str | None = None,
) -> Callable:
    """
    :returns: a callable that encapsulates the action to perform
    """
    if open_in_vim_extensions is None:
        open_in_vim_extensions = set()

    if target is not None:
        target = URI(target.strip())

    if not target:
        _log.info("no target")
        return NoOp(target)

    if target.startswith("#"):
        return JumpToAnchor(target)

    if has_scheme(target):
        _log.debug(f"has scheme -> open in browser: {target=}")
        return BrowserOpen(target)

    if not has_extension(target, open_in_vim_extensions):
        _log.info("has no extension for opening in vim, opening with OS.")
        return OSOpen(target)

    if target.startswith("|filename|"):
        target = target[len("|filename|") :]

    if target.startswith("{filename}"):
        target = target[len("{filename}") :]

    return VimOpen(target)


def has_extension(path, extensions):
    if not extensions:
        return True  # TODO: Why??

    path = parse_uri(path)
    _, ext = os.path.splitext(path.path)
    return ext in extensions


def has_scheme(target) -> bool:
    scheme, netloc, path, params, query, fragment = urlparse(target)
    if scheme and path.isdigit():
        return False
    # not working with 3.10: https://stackoverflow.com/questions/1737575/are-colons-allowed-in-urls
    # return bool(urlparse(target).scheme)
    return bool(scheme)


@dataclass
class Action:
    target: Optional[URI]


class NoOp(Action):
    def __call__(self):
        print("<mdnav: no link>")


class BrowserOpen(Action):
    def __call__(self):
        print("<mdnav: open browser tab>")
        webbrowser.open_new_tab(self.target)


class OSOpen(Action):
    def __call__(self):
        p = parse_uri(self.target)
        if not Path(p.fullpath).exists():
            _log.error(f"{p} [{p.fullpath}] does not exists")
            raise FileNotFoundError(f"{p} [{p.fullpath}] does not exists")
        _log.debug(f"Opening {p.fullpath=}")

        if sys.platform.startswith("linux"):
            call(["xdg-open", p.fullpath])
        elif sys.platform.startswith("darwin"):
            call(["open", p.fullpath])
        else:
            os.startfile(p.fullpath)  # doubleclick equivalent


class VimOpen(Action):
    def __call__(self):
        # noinspection PyUnresolvedReferences
        import vim

        path = parse_uri(self.target)
        if not Path(path.fullpath).exists():
            _log.info(f"{path.fullpath=} does not exists. Creating...")
            # raise FileNotFoundError(f"{path.fullpath=} does not exists")
        _log.debug(f"Opening {path.fullpath=}")

        # TODO: make space handling more robust?
        p_sanitized = path.fullpath.replace(" ", "\\ ")
        vim.command(f"tabnew {p_sanitized}")
        if path.line is not None:
            try:
                line = int(path.line)
            except ValueError:
                print("invalid line number")
                return

            else:
                vim.current.window.cursor = (line, 0)

        if path.anchor is not None:
            JumpToAnchor(URI(path.anchor))()


class JumpToAnchor(Action):
    HEADING_PATTERN = re.compile(r"^#+(?P<title>.*)$")
    ATTR_LIST_PATTERN = re.compile(r"{:\s+#(?P<id>\S+)\s")

    def __call__(self):
        # noinspection PyUnresolvedReferences
        import vim

        _log.debug(f"{self.target=}")
        line = self.find_anchor(self.target, vim.current.buffer)
        _log.debug(f"{line=}")

        if line is None:
            return

        vim.current.window.cursor = (line + 1, 0)

    @classmethod
    def find_anchor(cls, target, buffer) -> int:
        needle = cls.norm_target(target)
        _log.debug(f"{target=}, {needle=}, {buffer=}")

        for idx, line in enumerate(buffer):
            m = cls.HEADING_PATTERN.match(line)
            if m is not None:
                title = m.group("title")
                anchor = cls.title_to_anchor(title)
                _log.debug(f"{title=}, {anchor=}")
                if anchor.startswith(needle):
                    return idx

            m = cls.ATTR_LIST_PATTERN.search(line)
            if m is not None and needle == m.group("id"):
                return idx

    @staticmethod
    def title_to_anchor(title) -> str:
        PUNCTUATION_TO_REMOVE = (
            "!\"#$%&'()*+,./:;<=>?@[\\]^_`{|}~"  # string.punctuation, keep -
        )
        title = title.translate(str.maketrans("", "", PUNCTUATION_TO_REMOVE))
        return "-".join(fragment.lower() for fragment in title.split())

    # @staticmethod
    @classmethod
    def norm_target(cls, target):
        if target.startswith("#"):
            target = target[1:]

        # be more lenient and allow not only anchors but also headings
        # return target.lower()
        return cls.title_to_anchor(target)


def call(args):
    """If available use vims shell mechanism to work around display issues"""
    try:
        import vim
    except ImportError:
        subprocess.call(args)
    else:
        subprocess.call(args)
        # Triggers prompt on vim, not good!
        # args = ["shellescape(" + json.dumps(arg) + ")" for arg in args]
        # vim.command('execute "! " . ' + ' . " " . '.join(args))


def check_path(line: str, pos: int) -> Tuple[str | None, int]:
    """Check if the cursor is on a path and return the path and the relative cursor position."""
    if len(line) <= pos:
        return None, 0
    if line[pos] in " \t":
        return None, pos
    start = line[:pos].rfind(" ") + 1  # handles also the case with pos == 0

    # TODO: handle escapes
    if start < 0:
        return None, pos

    end = line[start:].find(" ")
    if end < 0:
        end = len(line)

    path = line[start : start + end]
    try:
        p = Path(path)
        if any(
            [
                c
                for c in ["*", "?", "[", "]", "|", '"', "'", "<", ">", "!"]
                if c in str(p)
            ]
        ):
            raise ValueError(f"Skipping {p} because it contains an invalid character.")
        return path, pos - start
    except ValueError:
        _log.debug(f"Skipping {p} because it contains a non-path character.")
        return None, pos


@dataclass
class MdnavMatch:
    start: int  # start index of the match
    end: int  # exclusive
    url: str


def check_url(line: str, column: int) -> Tuple[str | None, int]:
    urls = []
    matches = re.finditer(URL_PATTERN, line)
    for match in matches:
        urls.append(
            MdnavMatch(
                start=match.start(),
                end=match.end(),
                url=match.group(),
            )
        )
        matched = match.group()
        if match.start() <= column < match.end():
            if matched.endswith(")"):  # is markdown link
                return None, column
            _log.debug(f"{urls=}")
            return matched, column - match.start()
    return None, column


def check_md_link(line: str, column: int) -> Tuple[str | None, int]:
    urls = []
    matches = re.finditer(MD_LINK_PATTERN, line)
    for match in matches:
        urls.append(
            MdnavMatch(
                start=match.start(),
                end=match.end(),
                url=match.group(2),
            )
        )
        if match.start() <= column < match.end():
            _log.debug(f"{urls=}")
            return match.group(2), column - match.start()
    return None, column


def check_reference_link(line: str, column: int) -> Tuple[str | None, int]:
    m = REFERENCE_DEFINITION_PATTERN.match(line)
    if m is not None:
        return m.group("link"), column
    return None, column


def parse_line(cursor, lines) -> URI | None:
    """Extract URI under cursor from text line"""
    row, column = cursor
    line = lines[row]

    _log.debug("handle line %s (%s, %s)", line, row, column)

    ### 1. Return with URL
    link_text, rel_column = check_url(line, column)
    if link_text is not None:
        return URI(link_text.strip())

    ### 2. Return with Markdown Reference Link
    link_text, rel_column = check_reference_link(line, column)
    if link_text is not None:
        return URI(link_text.strip())

    ### 3. Return with local path
    link_text, rel_column = check_path(line, column)
    if link_text is not None:
        return URI(link_text)

    ### 4. Parse Markdown Link
    link_text, rel_column = select_from_start_of_link(line, column)

    if not link_text:
        _log.info("could not find link text")
        return None

    m = LINK_PATTERN.match(link_text)

    if not m:
        _log.info("does not match link pattern")
        return None

    if m.end("link") <= rel_column:
        _log.info("cursor outside link")
        return None

    _log.debug("found match: %s", m.groups())
    assert (m.group("direct") is None) != (m.group("indirect") is None)

    if m.group("direct") is not None:
        _log.debug("found direct link: %s", m.group("direct"))
        return m.group("direct")

    _log.debug("follow indirect link %s", m.group("indirect"))
    indirect_ref = m.group("indirect")
    if not indirect_ref:
        indirect_ref = m.group("text")

    indirect_link_pattern = re.compile(r"^\[" + re.escape(indirect_ref) + r"\]:(.*)$")

    for line in lines:
        m = indirect_link_pattern.match(line)

        if m:
            return URI(m.group(1).strip())

    _log.info("could not match for indirect link")
    return None


def select_from_start_of_link(line, pos) -> Tuple[str | None, int]:
    """Return the start of the link string and the new cursor"""
    if pos < len(line) and line[pos] == "[":
        start = pos

    else:
        start = line[:pos].rfind("[")

    # TODO: handle escapes

    if start < 0:
        return None, pos

    # check for indirect links
    if start != 0 and line[start - 1] == "]":
        alt_start = line[:start].rfind("[")
        if alt_start >= 0:
            start = alt_start

    return line[start:], pos - start
