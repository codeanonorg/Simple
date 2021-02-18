"""
 Copyright (c) 2021 SolarLiner, jdrprod, Arxaqapi

 This software is released under the MIT License.
 https://opensource.org/licenses/MIT
"""

import logging
import json
from textwrap import wrap

from functools import partial
from typing import List, Literal, Optional, Union
from pathlib import Path
from argparse import ArgumentParser, ArgumentTypeError, Namespace
from dataclasses import dataclass

from .document import Document
from .exceptions import ProcessException
from .logs import create_logger
from .html import html


@dataclass
class Options:
    input: Path
    output: Path
    data: Optional[Path]
    log_level: int


def filepath(mode: Union[Literal["read"], Literal["write"]], s: str) -> Path:
    if s == "-":
        raise ArgumentTypeError(
            "\n\t".join(
                wrap(
                    f"Reading from stdin is not supported. Please use the `<(command)` shell syntax, which provides a temporary file path containing `command`'s standard output, to chain data from other commands."
                )
            )
        )
    p = Path(s)
    if mode == "read":
        try:
            p.open("r")
        except IOError as ex:
            raise ArgumentTypeError(f"Cannot open file '{p}': {ex}")
    if mode == "write":
        if p.is_dir():
            raise ArgumentTypeError(f"Cannot write to '{p}': Path leads to a directory")
    return p.absolute()


def parse_args(args: List[str]) -> Options:
    parser = ArgumentParser()
    parser.add_argument(
        "input",
        nargs=1,
        type=partial(filepath, "read"),
        help="Input HTML file to process",
    )
    parser.add_argument(
        "-o",
        "--output",
        required=True,
        nargs=1,
        type=partial(filepath, "write"),
        help="Output file path",
    )
    parser.add_argument(
        "-d",
        "--data",
        nargs="?",
        type=partial(filepath, "read"),
        help="Optional data in the form of a JSON file",
    )
    parser.add_argument(
        "-v", action="count", default=0, help="Increase verbosity level"
    )
    parsed: Namespace = parser.parse_args(args[1:])
    return Options(
        parsed.input[0], parsed.output[0], parsed.data, logging.WARN - parsed.v * 10
    )


def main(args: List[str]) -> int:
    opts = parse_args(args)
    logger = create_logger(opts.log_level)

    if opts.data is not None:
        with opts.data.open("rt") as d:
            data = json.load(d)
    else:
        data = {}
    try:
        doc = Document(opts.input)
        with opts.output.open("wt") as f:
            logger.info(f"Writing output to '{opts.output}'")
            f.write(html(doc.render(data)))
    except ProcessException as ex:
        ex.doc.adapter.critical(
            str(ex.exn),
            exc_info=None if opts.log_level > logging.DEBUG else ex,
            **ex.extra,
        )
        return 1
    except Exception as ex:
        logger.critical(
            f"Fatal error: {ex}",
            exc_info=None if opts.log_level > logging.DEBUG else ex,
        )
        return 1

    return 0


def run():
    import sys

    sys.exit(main(sys.argv))
