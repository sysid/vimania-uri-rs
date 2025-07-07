import logging
import os
from pathlib import Path

_log = logging.getLogger("vimania-uri_.environment")
ROOT_DIR = Path(__file__).parent.absolute()


class Environment:
    def __init__(self):
        self.log_level = os.environ.get("LOG_LEVEL", "INFO")


config = Environment()
