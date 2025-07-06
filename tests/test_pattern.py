import re

import pytest


@pytest.mark.parametrize(
    ("line", "result"),
    (
        ("[testuri](vm::http://www.test.org)", "http://www.test.org"),
        ("asdf http://www.google.com asdf", "http://www.google.com"),
        ("balaser https://my.net asdf", "https://my.net"),
        ("[testuri](vm::http://www.test.org) adf", "http://www.test.org"),
        (
            "[testuri](vm::http://www.test.org#adf?asdf&xxxx aaaaaaa",
            "http://www.test.org#adf?asdf&xxxx",
        ),
        ("[testuri](vm::http://www.test.org)adf", "http://www.test.org"),
    ),
)
def test_url_pattern_extraction(mocker, line, result):
    # Test URL pattern extraction functionality
    assert (
        re.compile(
            r""".*(https?:\/\/[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9]{1,6}\b[-a-zA-Z0-9@:%_\+.~#?&\/=]*)"""
        )
        .match(line)
        .group(1)
        == result
    )
