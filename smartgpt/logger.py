import logging
import sys


class CustomFormatter(logging.Formatter):
    """Logging Formatter to add colors"""

    blue = "\x1b[34;1m"
    yellow = "\x1b[33;1m"
    green = "\x1b[32;1m"
    reset = "\x1b[0m"
    format_str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    def format(self, record):
        record.levelname = self.green + record.levelname + self.reset
        record.name = self.blue + record.name + self.reset
        return super().format(record)

    def formatMessage(self, record):
        # Override asctime in the format string with the colorized version
        return self.format_str % {
            "asctime": self.yellow + self.formatTime(record, self.datefmt) + self.reset,
            "name": record.name,
            "levelname": record.levelname,
            "message": record.getMessage(),
        }


logger = logging.getLogger(name="SmartGPT")
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(CustomFormatter())
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)
