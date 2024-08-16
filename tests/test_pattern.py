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
def test_delete_twbm_regexp(mocker, line, result):
    # https://regex101.com/r/W9Epg0/1
    # https://regex101.com/delete/gn3L5TNGXye9ajzZf5szoY5G
    # spy = mocker.patch("vimania.core.BukuDb")
    # delete_twbm(line)
    assert (
        re.compile(
            r""".*(https?:\/\/[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9]{1,6}\b[-a-zA-Z0-9@:%_\+.~#?&\/=]*)"""
        )
        .match(line)
        .group(1)
        == result
    )
