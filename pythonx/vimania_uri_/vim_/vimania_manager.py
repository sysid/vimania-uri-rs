import logging
import traceback
import vimania_uri_rs  # must be after logging setup
from functools import wraps
from pathlib import Path
from pprint import pprint
from typing import Dict, Tuple

from vimania_uri_ import md
from vimania_uri_.exception import VimaniaException
from vimania_uri_.pattern import URL_PATTERN
from vimania_uri_.vim_ import vim_helper

""" Python VIM Interface Wrapper """

_log = logging.getLogger("vimania-uri.vimania_manager")
ROOT_DIR = Path(__file__).parent.absolute()

try:
    # import vim  # relevant for debugging, but gives error when run with main
    # noinspection PyUnresolvedReferences
    import vim
except:  # noqa
    _log.debug("No vim module available outside vim")
    pass


def split_path(args: str) -> Tuple[str, str]:
    if "#" not in args:
        return args, ""
    path, *suffix = args.split("#", 1)
    suffix = "".join(suffix)
    if Path(path).suffix == ".md":
        suffix = f"#{suffix}"  # add the leading heading marker back again
    return path, suffix


def err_to_scratch_buffer(func):
    """Decorator that will catch any Exception that 'func' throws and displays
    it in a new Vim scratch buffer."""

    # Gotcha: static function, so now 'self'
    @wraps(func)
    def wrapper(*args, **kwds):
        # noinspection PyBroadException
        try:
            return func(*args, **kwds)
        except Exception as _:  # pylint: disable=bare-except
            msg = """An error occured.

Following is the full stack trace:
"""
            msg += traceback.format_exc()
            vim_helper.new_scratch_buffer(msg)

    return wrapper


def warn_to_scratch_buffer(func):
    """Decorator that will catch any Exception that 'func' throws and displays
    it in a new Vim scratch buffer."""

    # Gotcha: static function, so now 'self'
    @wraps(func)
    def wrapper(*args, **kwds):
        try:
            return func(*args, **kwds)
        except VimaniaException as e:  # pylint: disable=bare-except
            msg = str(e)
            vim_helper.new_scratch_buffer(msg)

    return wrapper


class VimaniaUriManager:
    def __init__(
        self,
        *,
        extensions=None,
        twbm_integrated=False,
        plugin_root_dir=None,
    ):
        self.extensions = extensions
        self.twbm_integrated = twbm_integrated
        self.plugin_root_dir = plugin_root_dir
        _log.debug(f"{extensions=}, {plugin_root_dir=}")

    def __repr__(self):
        return "{self.__class__.__name__}"  # subclassing!

    @staticmethod
    def _get_locals() -> Dict[str, any]:
        locals = {
            "window": vim.current.window,
            "buffer": vim.current.buffer,
            "line": vim.current.window.cursor[0] - 1,
            "column": vim.current.window.cursor[1] - 1,
            "cursor": vim.current.window.cursor,
        }
        if _log.getEffectiveLevel() == logging.DEBUG:
            # print(vim.vars.keys())
            # print(vim.VIM_SPECIAL_PATH)
            # print(vim._get_paths())
            pprint(locals)
        return locals

    @err_to_scratch_buffer
    @warn_to_scratch_buffer
    def call_handle_md2(self, save_twbm: str):
        return_message = ""
        _log.debug(f"{save_twbm=}")

        row, col = vim.current.window.cursor
        cursor = (row - 1, col)
        lines = vim.current.buffer

        current_file = (vim.eval("expand('%:p')"),)
        target = md.parse_line(cursor, lines)
        _log.debug(f"open {target=} from {current_file=}")

        action = md.open_uri(
            target,
            open_in_vim_extensions=self.extensions,
            save_twbm=False if int(save_twbm) == 0 else True,
            twbm_integrated=self.twbm_integrated,
        )
        action()
        if return_message != "":
            vim.command(f"echom '{return_message}'")

    @staticmethod
    @err_to_scratch_buffer
    def debug():
        current = vim.current

        locals = VimaniaUriManager._get_locals()
        # add line at end of buffer
        current.buffer[-1:0] = ["New line at end."]

    @staticmethod
    @err_to_scratch_buffer
    def throw_error(args: str, path: str):
        _log.debug(f"{args=}, {path=}")
        raise Exception(f"Exception Test")

    @staticmethod
    @err_to_scratch_buffer
    def edit_vimania(args: str):
        """Edits text files and jumps to first position of pattern
        pattern is extracted via separator: '#'

        -- DEPRECATED --
        """
        assert isinstance(args, str), f"Error: input must be string, got {type(args)}."

        path, suffix = split_path(args)
        _log.debug(f"{args=}, {path=}, {suffix=}")
        vim.command(f"tabnew {path}")
        if suffix != "":
            vim.command(f"/{suffix}")

    @staticmethod
    @err_to_scratch_buffer
    def get_url_title(url: str):
        """Edits text files and jumps to first position of pattern
        pattern is extracted via separator: '#'
        """
        m = URL_PATTERN.match(url)
        if m is None:
            _log.warning(f"Invalid URL: {url=}")
            vim.command(f"echom 'Invalid URL: {url=}'")
        assert isinstance(url, str), f"Error: input must be string, got {type(url)}."
        # _log.debug(f"{url=}")
        try:
            title = vimania_uri_rs.get_url_title(url)
            # https://stackoverflow.com/a/27324622
            title = title.replace("'", "''")
            _log.debug(f"{title=}")
            vim.command(f"let g:vimania_url_title = '{str(title)}'")
        except Exception as e:
            _log.warning(f"Invalid URL: {url=}, {e=}")
            vim.command(f"echom 'Invalid URL: {url=}'")
