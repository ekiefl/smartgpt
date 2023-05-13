import logging
import sys
import time


class CustomFormatter(logging.Formatter):
    """Logging Formatter to add colors"""

    blue = "\x1b[34;1m"
    yellow = "\x1b[33;1m"
    green = "\x1b[32;1m"
    reset = "\x1b[0m"

    def format(self, record):
        record.levelname = self.green + record.levelname + self.reset
        record.name = self.blue + record.name + self.reset
        record.asctime = (
            self.yellow + self.formatTime(record, self.datefmt) + self.reset
        )
        return logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        ).format(record)


logger = logging.getLogger(name="SmartGPT")
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(CustomFormatter())
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)
