import os
from dataclasses import dataclass
from pathlib import Path
from re import search
import sys
import logging
from typing import List, MutableMapping, Optional, Tuple

FORMAT = "%(levelname)s: %(message)s"


class DocumentLogAdapter(logging.LoggerAdapter):
    def __init__(
        self, logger: logging.Logger, document: "Simple.document.Document"  # type: ignore
    ) -> None:
        super().__init__(logger, {"document": document})

    def process(self, msg: str, kwargs: MutableMapping) -> Tuple[str, MutableMapping]:
        from .document import Document

        cwd = Path.cwd()
        doc: Document = self.extra["document"]
        relpath = doc.path.relative_to(cwd)
        include_stack = self._get_include_stack()
        if len(include_stack) > 0:
            incstack_str = "\n\t" + "\n\t".join(
                "included from " + str(s.relative_to(cwd)) for s in include_stack
            )
        else:
            incstack_str = ""
        extra = {"document": doc, "include-stack": include_stack}
        if "pos" in kwargs:
            (line, col) = kwargs["pos"]
            return f"{relpath}:{line}:{col} {msg}{incstack_str}", {
                **kwargs,
                "extra": extra,
            }
        else:
            return f"{relpath}: {msg}{incstack_str}", {**kwargs, "extra": extra}

    def _get_include_stack(self):
        from .document import Document

        doc: Document = self.extra["document"]
        include_stack: List[Path] = []
        while (parent := doc.parent) is not None:
            include_stack.append(parent.path)
            doc = doc.parent
        return include_stack


class ColoredFormatter(logging.Formatter):
    COLOR_RED = "\033[1;31m"
    COLOR_GREEN = "\033[1;32m"
    COLOR_YELLOW = "\033[1;33m"
    COLOR_MAGENTA = "\033[1;35m"
    COLOR_BLUE = "\033[36m"
    COLOR_NEUTRAL = "\033[0m"

    COLORS = {
        "CRITICAL": COLOR_RED,
        "ERROR": COLOR_RED,
        "WARNING": COLOR_MAGENTA,
        "INFO": COLOR_YELLOW,
        "DEBUG": COLOR_BLUE,
    }

    def __init__(self, msg, use_color=True):
        logging.Formatter.__init__(self, msg)
        self.use_color = use_color

    def format(self, record: logging.LogRecord):
        levelname = record.levelname
        # Prettify the levelname
        name = levelname[0].upper() + levelname[1:].lower()
        # Colorize the levelname
        if self.use_color:
            record.levelname = f"{self.COLORS[levelname]}{name}{self.COLOR_NEUTRAL}"
        else:
            record.levelname = name

        return super().format(record)


def create_logger(log_level: int):
    logger = logging.getLogger()
    logger.setLevel(log_level)
    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(ColoredFormatter(FORMAT))
    logger.addHandler(handler)
    return logger
