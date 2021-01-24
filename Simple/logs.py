import sys
import logging

FORMAT = "[%(name)s] %(levelname)s %(message)s"


class ColoredFormatter(logging.Formatter):
    def __init__(self, msg, use_color=True):
        logging.Formatter.__init__(self, msg)
        self.use_color = use_color

    def format_level(self, levelname: str):
        return levelname[0] + levelname[1:].lower()

    def format(self, record):
        levelname = record.levelname
        if self.use_color:
            record.levelname = "\033[1;31m" + \
                self.format_level(levelname) + "\033[0m"

        return logging.Formatter.format(self, record)


def create_logger(log_level: int):
    logger = logging.getLogger()
    logger.setLevel(log_level)
    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(ColoredFormatter(FORMAT))
    logger.addHandler(handler)
