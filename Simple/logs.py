import logging


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


class ColoredLogger(logging.Logger):
    FORMAT = "[%(name)s] %(levelname)s %(message)s"

    def __init__(self, name):
        logging.Logger.__init__(self, name, logging.DEBUG)

        color_formatter = ColoredFormatter(self.FORMAT)

        console = logging.StreamHandler()
        console.setFormatter(color_formatter)

        self.addHandler(console)
        return


logging.setLoggerClass(ColoredLogger)
