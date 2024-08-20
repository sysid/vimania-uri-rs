import logging
import os
from pathlib import Path
from typing import Optional

_log = logging.getLogger("vimania-plugin.environment")
ROOT_DIR = Path(__file__).parent.absolute()


class Environment:
    def __init__(self):
        self.log_level = os.environ.get("LOG_LEVEL", "INFO")
        self.twbm_db_url = os.environ.get("BKMR_DB_URL", None)

    @property
    def is_installed_twbm(self):
        return self.twbm_db_url is not None


config = Environment()
_ = None
