import os
from pathlib import Path

import pytest
from vimania_uri_.environment import ROOT_DIR
from vimania_uri_.md import mdnav
from vimania_uri_.md.mdnav import URI


def _find_cursor(lines):
    lines_without_cursor = []
    cursor = None

    for row, line in enumerate(lines):
        pos = line.find("^")

        if pos < 0:
            lines_without_cursor.append(line)

        else:
            cursor = (row, pos)
            lines_without_cursor.append(line[:pos] + line[pos + 1 :])

    return cursor, lines_without_cursor


class TestParseLine:
    # NOTE: the cursor is indicated with ^, the cursor will be placed on the
    # following character
    parse_link_cases = [
        # default cases
        (["foo ^[bar](baz.md)"], "baz.md"),
        (["foo [bar](baz.md^)"], "baz.md"),
        (["foo [b^ar](baz.md)"], "baz.md"),
        (["foo [b^ar](baz.md) [bar](bar.md)"], "baz.md"),
        (["foo [b^ar][bar]", "[bar]: baz.md"], "baz.md"),
        (["foo [b^ar][bar]", "[bar]: |filename|./baz.md"], "|filename|./baz.md"),
        (
            ["foo [b^ar][bar] [bar][baz]", "[bar]: |filename|./baz.md"],
            "|filename|./baz.md",
        ),
        (
            ["foo [b^ar][bar] [bar][baz]", "[bar]: {filename}./baz.md"],
            "{filename}./baz.md",
        ),
        # # empty link target
        (["foo [b^ar][]", "[bar]: baz.md"], "baz.md"),
        (["foo [@b^ar][]", "[@bar]: baz.md"], "baz.md"),
        (["foo [^@bar][]", "[@bar]: baz.md"], "baz.md"),
        # cursor outside link area
        (["foo [bar](baz.md)^"], None),  # cursor outside of line
        (["foo^  [bar](baz.md) "], None),
        (["foo ^ [bar](baz.md) "], None),
        (["foo [bar](baz.md) ^ "], None),
        (["foo [bar](baz.md)^  "], None),
        # # cursor inside target part
        (["foo [bar][b^ar]", "[bar]: baz.md"], "baz.md"),
        (["foo [bar](b^az.md) [bar](bar.md)"], "baz.md"),
        (["foo [bar](baz.md) [bar](^bar.md)"], "bar.md"),
        # malformed links
        (["][b^ar](bar.md)"], "bar.md"),
        # empty line
        (["^"], None),
        # multiple [] pairs across multiple lines (reference style links)
        (
            ["- [ ] checkout [la^bel][target] abs", "[target]: example.com"],
            "example.com",
        ),
        (
            ["- [ ] checkout [label]^[target] abs", "[target]: example.com"],
            "example.com",
        ),
        (
            ["- [ ] checkout [label][tar^get] abs", "[target]: example.com"],
            "example.com",
        ),
        # reference definitions
        (["[f^oo]: test.md"], "test.md"),
        (["[foo]: test.md^"], "test.md"),
        (["[foo]: ^test.md"], "test.md"),
        (["^[foo]: test.md"], "test.md"),
        # blank URLs
        (["https://^www.google.com"], "https://www.google.com"),
        (
            ["some other stuff, not &%$ https://^www.google.com   .. and more"],
            "https://www.google.com",
        ),
        # With Variables
        (["[md-doc]($HO^ME/vimwiki/help.md)"], "$HOME/vimwiki/help.md"),
        # path with spaces
        (["[]('$HO^ME/vimwiki bla/help.md')"], "'$HOME/vimwiki bla/help.md'"),
    ]

    @pytest.mark.parametrize("lines, expected", parse_link_cases)
    def test_parse_line(self, lines, expected):
        cursor, mod_lines = _find_cursor(lines)
        actual = mdnav.parse_line(cursor, mod_lines)
        assert actual == expected

    @pytest.mark.parametrize(
        ("line", "expected"),
        (
            ("^$HOME/xxx", "$HOME/xxx"),
            ("^$HOME/xxx bla blub", "$HOME/xxx"),
            ("$HOME/xxx bl^a blub", "bla"),
            ("my line $HO^ME/xxx bla blub", "$HOME/xxx"),
            ("my 'line' $HOME/xxx^ bla blub'", None),
            ("foo^  [bar](baz.md) ", None),
            # invalid path
            ("^$HOME/xxx|blub", None),
        ),
    )
    def test_check_path(self, line, expected):
        cursor, mod_lines = _find_cursor([line])
        assert len(mod_lines) == 1, f"too many lines: {mod_lines=}"

        link_text, rel_column = mdnav.check_path(mod_lines[0], cursor[1])
        assert link_text == expected

    @pytest.mark.parametrize(
        ("line", "expected"),
        (
            ("^http://yyy/xxx", "http://yyy/xxx"),
            ("http://yyy/xxx^", None),
            ("htt://yyy/^xxx", None),
            (
                "Google: https://^www.google.com and here to Wikipedia: https://en.wikipedia.org",
                "https://www.google.com",
            ),
            (
                "Google: https://www.google.com and here to Wikipedia: http://en.wikipedia.or^g",
                "http://en.wikipedia.org",
            ),
            (" ^https://www.google.com/?q=xxx  xxxx", "https://www.google.com/?q=xxx"),
            ("[xx](http://^yyy/xxx)", None),  # do not match markdown links
        ),
    )
    def test_check_url(self, line, expected):
        cursor, mod_lines = _find_cursor([line])
        assert len(mod_lines) == 1, f"too many lines: {mod_lines=}"

        link_text, rel_column = mdnav.check_url(mod_lines[0], cursor[1])
        assert link_text == expected

    @pytest.mark.parametrize(
        ("line", "expected"), (("^[xxx](http://yyy/xxx)", "http://yyy/xxx"),)
    )
    def test_check_md(self, line, expected):
        cursor, mod_lines = _find_cursor([line])
        assert len(mod_lines) == 1, f"too many lines: {mod_lines=}"

        link_text, rel_column = mdnav.check_md_link(mod_lines[0], cursor[1])
        assert link_text == expected


open_uri_cases = [
    (None, {}, mdnav.NoOp(None)),
    ("baz.md", {}, mdnav.VimOpen(URI("baz.md"))),
    ("baz.md:20", {}, mdnav.VimOpen(URI("baz.md:20"))),
    ("baz.MD", {"open_in_vim_extensions": [".md"]}, mdnav.OSOpen(URI("baz.MD"))),
    ("baz.md", {"open_in_vim_extensions": [".md"]}, mdnav.VimOpen(URI("baz.md"))),
    ("baz.md:20", {"open_in_vim_extensions": [".md"]}, mdnav.VimOpen(URI("baz.md:20"))),
    ("|filename|/foo/baz.md", {}, mdnav.VimOpen(URI("/foo/baz.md"))),
    ("{filename}/foo/baz.md", {}, mdnav.VimOpen(URI("/foo/baz.md"))),
    ("/foo/bar.md", {}, mdnav.VimOpen(URI("/foo/bar.md"))),
    ("http://example.com", {}, mdnav.BrowserOpen(URI("http://example.com"))),
    (
        "http://example.com",
        {"open_in_vim_extensions": [".md"]},
        mdnav.BrowserOpen(URI("http://example.com")),
    ),
    ("$HOME", {"open_in_vim_extensions": [".md"]}, mdnav.OSOpen(URI("$HOME"))),
]


@pytest.mark.parametrize("target, open_link_kwargs, expected", open_uri_cases)
def test_open_uri(target, open_link_kwargs, expected):
    actual = mdnav.open_uri(URI(target), **open_link_kwargs)
    assert actual == expected


jump_to_anchor_cases = [
    ("#foo", ["a", "# foo", "b"], 1),
    ("#foo-bar-baz", ["a", "#  Foo  BAR  Baz", "b"], 1),
    # be more lenient and allow not only anchors but also headings
    (
        "Battle of the datacontainers, Serialization",
        ["a", "### Battle of the datacontainers, Serialization", "b"],
        1,
    ),
    (
        "Battle of the datacontainers Serialization",
        ["a", "### Battle of the datacontainers, Serialization", "b"],
        1,
    ),
    (
        "Battle of the datacontainers, Serialization",
        ["a", "### Battle of the datacontainers, Serialization and more", "b"],
        1,
    ),
    ("#foo", ["a", "#  Bar", "b"], None),
    ("#Foo-Bar-Baz", ["a", "### Foo Bar Baz", "b"], 1),
    # use attr-lists to define custom ids
    ("#hello-world", ["a", "### Foo Bar Baz {: #hello-world } ", "b"], 1),
    # first match wins
    ("#hello-world", ["# hello world", "### Foo Bar Baz {: #hello-world } ", "b"], 0),
]


@pytest.mark.parametrize("target, buffer, expected", jump_to_anchor_cases)
def test_jump_to_anchor(target, buffer, expected):
    actual = mdnav.JumpToAnchor.find_anchor(target, buffer)
    assert actual == expected


class TestParseUri:
    @pytest.mark.parametrize(
        "path, expected_path, expected_line, expected_anchor, expected_scheme, expected_fullpath",
        [
            (None, "", None, None, None, ""),
            (
                "foo.md",
                "./foo.md",
                None,
                None,
                None,
                str(ROOT_DIR.parent.parent / "foo.md"),
            ),
            ("foo:bar.md", "foo:bar.md", None, None, "foo", "foo:bar.md"),
            (
                "foo.md:30",
                "./foo.md",
                "30",
                None,
                None,
                str(ROOT_DIR.parent.parent / "foo.md"),
            ),
            (
                "foo.md#hello-world",
                "./foo.md",
                None,
                "hello-world",
                None,
                str(ROOT_DIR.parent.parent / "foo.md"),
            ),
            (
                "foo.md#happy:)",
                "./foo.md",
                None,
                "happy:)",
                None,
                str(ROOT_DIR.parent.parent / "foo.md"),
            ),
            (
                "/home/xxx/foo.md#hello-world",
                "/home/xxx/foo.md",
                None,
                "hello-world",
                None,
                "/home/xxx/foo.md",
            ),
            (
                "~/foo.md#hello-world",
                "~/foo.md",
                None,
                "hello-world",
                None,
                str(Path.home() / "foo.md"),
            ),
            (
                "https://www.google.com/bla/blub",
                "https://www.google.com/bla/blub",
                None,
                None,
                "https",
                "https://www.google.com/bla/blub",
            ),
            ("xxx://aything", "xxx://aything", None, None, "xxx", "xxx://aything"),
            (
                "./xxx://yyy",
                "xxx:/yyy",
                None,
                None,
                None,
                str(ROOT_DIR.parent.parent / "xxx:/yyy"),
            ),
            (
                "./xxx/yyy",
                "xxx/yyy",
                None,
                None,
                None,
                str(ROOT_DIR.parent.parent / "xxx/yyy"),
            ),
        ],
    )
    def test_parse_uri(
        self,
        path,
        expected_path,
        expected_line,
        expected_anchor,
        expected_scheme,
        expected_fullpath,
    ):
        path = mdnav.parse_uri(path)

        assert path.path == expected_path
        assert path.line == expected_line
        assert path.anchor == expected_anchor
        assert path.scheme == expected_scheme
        assert path.fullpath == expected_fullpath

    def test_full_path(self, mocker):
        _ = mocker.patch.dict(os.environ, {"HOME": "/home/xxx"}, clear=True)
        path = mdnav.parse_uri(URI("~/foo.md#hello-world"))
        assert path.fullpath == "/home/xxx/foo.md"

        _ = mocker.patch.dict(os.environ, {"XXX": "/xxx"}, clear=True)
        path = mdnav.parse_uri(URI("$XXX/foo.md#hello-world"))
        assert path.fullpath == "/xxx/foo.md"

        path = mdnav.parse_uri(URI("$XXX_NOT_EXIST/foo.md#hello-world"))
        assert "$XXX_NOT_EXIST/foo.md" in path.fullpath
