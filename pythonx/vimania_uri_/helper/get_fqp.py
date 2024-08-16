import logging
import os
from pathlib import Path
from typing import Tuple

from vimania_uri_.exception import VimaniaException

_log = logging.getLogger(__name__)


def get_fqp(args: str) -> Tuple[str, str]:
    p = Path.home()  # default setting
    if args.startswith("http"):
        _log.debug(f"Http Link")
        p = args
    # next elif needed to group all possible pathes
    elif (
        args[0] in "/.~$0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    ):
        if args.startswith("/"):
            _log.debug(f"Absolute path.")
            p = Path(args)
        elif args.startswith("~"):
            _log.debug(f"Path with prefix tilde.")
            p = Path(args).expanduser().absolute()
        elif args.startswith("$"):
            _log.debug(f"Path with environment prefix.")
            p = Path(args)
            env_path = os.getenv(p.parts[0].strip("$"), None)
            if env_path is None:
                _log.warning(f"{p.parts[0]} not set in environment. Cannot proceed.")
                return str(p), f"{p.parts[0]} not set in environment. Cannot proceed."
            p = Path(env_path) / Path(*p.parts[1:])
        else:
            _log.debug(f"Relative path: {args}, working dir: {os.getcwd()}")
            p = Path(args).absolute()

        if not p.exists():
            _log.error(f"{p} does not exists.")
            raise VimaniaException(f"{p} does not exists")
    else:
        _log.error(f"Unknown protocol: {args=}")
        raise VimaniaException(f"Unknown protocol: {args=}")

    return str(p), ""
