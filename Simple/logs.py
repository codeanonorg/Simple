import sys
import logging

FORMAT = "[%(name)s] %(levelname)s %(message)s"


class ColoredFormatter(logging.Formatter):

    COLOR_RED = "\033[1;31m"
    COLOR_GREEN = "\033[1;32m"
    COLOR_YELLOW = "\033[1;33m"
    COLOR_MAGENTA = "\033[1;35m"
    COLOR_NEUTRAL = "\033[0m"

    COLORS = {
        "WARNING": COLOR_MAGENTA,
        "ERROR": COLOR_RED,
        "INFO": COLOR_YELLOW,
    }

    def __init__(self, msg, use_color=True):
        logging.Formatter.__init__(self, msg)
        self.use_color = use_color

    def format(self, record):
        levelname = record.levelname
        # Prettify the levelname
        name = levelname[0] + levelname[1:].lower()
        # Colorize the levelname
        if self.use_color:
            record.levelname = f"{self.COLORS[levelname]}{name}{self.COLOR_NEUTRAL}"
        else:
            record.levelname = name

        return logging.Formatter.format(self, record)


def create_logger(log_level: int):
    logger = logging.getLogger()
    logger.setLevel(log_level)
    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(ColoredFormatter(FORMAT))
    logger.addHandler(handler)
    return logger
