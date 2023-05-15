import logging
import sys

from smartgpt.datatypes import Verbosity


class CustomFormatter(logging.Formatter):
    """Logging Formatter to add colors"""

    blue = "\x1b[34;1m"
    yellow = "\x1b[33;1m"
    green = "\x1b[32;1m"
    reset = "\x1b[0m"
    format_str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    def format(self, record):
        record.levelname = self.yellow + record.levelname + self.reset
        record.name = self.blue + record.name + self.reset
        return super().format(record)

    def formatMessage(self, record):
        # Override asctime in the format string with the colorized version
        return self.format_str % {
            "asctime": self.green + self.formatTime(record, self.datefmt) + self.reset,
            "name": record.name,
            "levelname": record.levelname,
            "message": record.getMessage(),
        }


handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(CustomFormatter())


def get_logger(
    name: str = "SmartGPT", verbosity: Verbosity = Verbosity.SOME
) -> logging.Logger:
    logger = logging.getLogger(name=name)
    logger.addHandler(handler)
    logger.propagate = False

    if verbosity == Verbosity.NONE:
        logger.setLevel(logging.CRITICAL)
    elif verbosity == Verbosity.SOME:
        logger.setLevel(logging.INFO)
    elif verbosity == Verbosity.ALL:
        logger.setLevel(logging.DEBUG)
    else:
        raise NotImplementedError()

    return logger


default_logger = get_logger()
