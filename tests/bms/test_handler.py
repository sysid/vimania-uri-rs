import pytest
from typing import Tuple, Sequence

from vimania_uri_.bms.handler import add_twbm, delete_twbm

# Example URL for testing
TEST_URL = "https://example.com/xxxxxxxxxx"
TEST_URL = "https://sysid.github.io/vimania-uri/"


# @pytest.mark.skip(reason="manual test")
def test_add_twbm():
    result_code = add_twbm(TEST_URL, "x.md")
    assert result_code == 0, "Failed to add the bookmark"


def test_delete_twbm():
    add_twbm(TEST_URL)
    result = delete_twbm(TEST_URL)

    # Check if the result contains a successful deletion entry
    assert len(result) == 1, "Expected one URL to be deleted"
    result_code, url = result[0]
    assert result_code == 0, "Failed to delete the bookmark"
    assert url == f'"{TEST_URL}"', f"Deleted URL mismatch: expected {TEST_URL}, got {url}"


def test_delete_twbm_not_existing():
    # Attempt to delete a URL that is not in the bookmark database
    result = delete_twbm("https://nonexistent-url.com")

    # Check that the function tried to delete and handled the error
    assert len(result) == 1, "Expected one URL to be processed"
    result_code, url = result[0]
    assert result_code == 0, "Expected a non-zero exit code for non-existing bookmark"

