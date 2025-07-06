# This only runs once via re-sourcing
import logging
import os
import sys
from pprint import pprint

from vimania_uri_.vim_.vimania_manager import VimaniaUriManager

try:
    # import vim  # relevant for debugging, but gives error when run with main
    # noinspection PyUnresolvedReferences
    import vim
except:  # noqa
    print("-E- No vim module available outside vim")
    raise

if int(vim.eval("g:twvim_debug")) == 1:
    LOG_LEVEL = logging.DEBUG
else:
    LOG_LEVEL = logging.INFO

_log = logging.getLogger("vimania-uri_")

if not _log.handlers:  # avoid adding multiple handler via re-sourcing
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(
        logging.Formatter(
            "%(asctime)-15s.%(msecs)03d  %(levelname)s %(name)s %(funcName)s:%(lineno)d %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    )
    _log.addHandler(handler)
    _log.setLevel(LOG_LEVEL)

_log.debug("Starting Python")

# GOTCHA: activates other venvs as well
# this is not necessary any more with proper pythonx installation
if "VIRTUAL_ENV" in os.environ:
    _log.debug(f"Running in VENV: {os.environ['VIRTUAL_ENV']}")
    project_base_dir = os.environ["VIRTUAL_ENV"]
    activate_this = os.path.join(project_base_dir, "bin/activate_this.py")
    
    # Check if activate_this.py exists before trying to execute it
    if os.path.exists(activate_this):
        try:
            exec(open(activate_this).read(), {"__file__": activate_this})
            _log.debug(f"Successfully activated virtual environment: {project_base_dir}")
        except Exception as e:
            _log.warning(f"Failed to activate virtual environment {project_base_dir}: {e}")
    else:
        _log.debug(f"activate_this.py not found at {activate_this}, skipping virtual environment activation")
        _log.debug("Modern virtual environments don't require activate_this.py for plugin operation")

_log.debug(
    "------------------------------ Begin Python Init -------------------------------"
)
plugin_root_dir = vim.eval("s:script_dir")
_log.debug(f"{plugin_root_dir=}")
if LOG_LEVEL == logging.DEBUG:
    pprint(sys.path)
    print(f"{sys.version_info=}")
    print(f"{sys.prefix=}")
    print(f"{sys.executable=}")

if int(vim.eval("exists('g:vimania_uri_extensions')")):
    extensions = vim.eval("g:vimania_uri_extensions")
    # extensions = [ext.strip() for ext in extensions.split(',')]
else:
    extensions = None

if int(vim.eval("exists('g:vimania_uri_twbm_integration')")):
    twbm_integrated = vim.eval("g:vimania_uri_twbm_integration")
    twbm_integrated = True if int(twbm_integrated) == 1 else False
else:
    twbm_integrated = False

_log.debug(f"{extensions=}, {twbm_integrated=}")

xUriMgr = VimaniaUriManager(
    plugin_root_dir=plugin_root_dir,
    extensions=extensions,
    twbm_integrated=twbm_integrated,
)

_log.debug(
    "------------------------------ End Python Init -------------------------------"
)
