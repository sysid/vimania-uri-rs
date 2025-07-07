import logging

import pytest

"""
only import the module under test within the test function
to allow for patching the vim package
"""


@pytest.fixture
def mock_vim(mocker):
    # Create a mock object for the vim package
    mock_vim = mocker.MagicMock()
    mock_vim.command = mocker.MagicMock()
    mock_vim.current.window.cursor = (1, 1)
    mock_vim.current.buffer = ["https://www.google.com"]
    mock_vim.eval.return_value = "my_file.md"
    mocker.patch.dict("sys.modules", {"vim": mock_vim})
    return mock_vim


@pytest.mark.usefixtures("mock_vim")
class TestVimaniaUriManager:
    @pytest.mark.skip(reason="not applicable currently")
    def test_twbm(self, mocker, mock_vim):
        import vimania_uri_.vim_.vimania_manager as module_under_test

        # noinspection PyUnresolvedReferences
        assert module_under_test.vim == mock_vim

        mocked_add_twbm = mocker.patch(
            "vimania_uri_.vim_.vimania_manager.add_twbm", return_value=9999
        )
        mocked_open_uri = mocker.patch(
            "vimania_uri_.vim_.vimania_manager.md", autospec=True
        )

        vm = module_under_test.VimaniaUriManager(
            extensions=["vimwiki", "markdown", "pdf", "png", "jpg", "jpeg", "gif"],
            twbm_integrated=True,
            plugin_root_dir=None,
        )
        vm.call_handle_md2(save_twbm="1")
        mocked_add_twbm.assert_called_once()
        mocked_open_uri.open_uri.assert_called_once()

    @pytest.mark.skip(reason="not applicable currently")
    def test_twbm_not_configured(self, mocker, mock_vim):
        import vimania_uri_.vim_.vimania_manager as module_under_test

        # noinspection PyUnresolvedReferences
        assert module_under_test.vim == mock_vim

        mocked_add_twbm = mocker.patch(
            "vimania_uri_.vim_.vimania_manager.add_twbm", return_value=9999
        )
        mocked_open_uri = mocker.patch(
            "vimania_uri_.vim_.vimania_manager.md", autospec=True
        )

        vm = module_under_test.VimaniaUriManager(
            extensions=["vimwiki", "markdown", "pdf", "png", "jpg", "jpeg", "gif"],
            plugin_root_dir=None,
        )
        vm.call_handle_md2(save_twbm="1")
        mocked_open_uri.open_uri.assert_called_once()
        mocked_add_twbm.assert_not_called()

    def test_get_url_title(self, mocker, mock_vim, caplog):
        caplog.set_level(logging.DEBUG)

        import vimania_uri_.vim_.vimania_manager as module_under_test

        # noinspection PyUnresolvedReferences
        assert module_under_test.vim == mock_vim

        vm = module_under_test.VimaniaUriManager(
            extensions=["vimwiki", "markdown", "pdf", "png", "jpg", "jpeg", "gif"],
            plugin_root_dir=None,
        )
        vm.get_url_title("https://www.google.com")
        assert "Google" in caplog.text


@pytest.mark.parametrize(
    ("args", "path", "suffix"),
    (
        ("/home/user/bla", "/home/user/bla", ""),
        ("/home/user/bla#foo", "/home/user/bla", "foo"),
        ("/home/user/bla.md#foo", "/home/user/bla.md", "#foo"),
        ("/home/user/bla.md#foo##blub", "/home/user/bla.md", "#foo##blub"),
        ("/home/user/bla.md#foo##blub blank", "/home/user/bla.md", "#foo##blub blank"),
    ),
)
def test_split_path(args, path, suffix):
    from vimania_uri_.vim_.vimania_manager import split_path

    assert split_path(args) == (path, suffix)


# def test_clean_url_tilte():
#     title = r"Improve Your Code's Maintainability"
#     title = title.replace("'", "''")
#     assert True
