"""
 Copyright (c) 2021 SolarLiner, jdrprod, Arxaqapi
 
 This software is released under the MIT License.
 https://opensource.org/licenses/MIT
"""

import logging

from functools import partial
from typing import List, Literal, Union
from pathlib import Path
from argparse import ArgumentParser, ArgumentTypeError
from dataclasses import dataclass

from .document import Document
from .exceptions import ProcessedException
from .logs import create_logger


@dataclass
class Options:
    input: Path
    output: Path
    log_level: int


def filepath(
    mode: Union[Literal["read"], Literal["write"]], s: str
) -> Union[Path, Literal["stdio"]]:
    if s == "-":
        return "stdio"

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
    parser = ArgumentParser(prog=__name__)
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
        "-v", action="count", default=0, help="Increase verbosity level"
    )
    args = parser.parse_args(args[1:])
    return Options(args.input[0], args.output[0], logging.WARN - args.v * 10)


def main(args: List[str]) -> int:
    opts = parse_args(args)
    logger = create_logger(opts.log_level)

    try:
        doc = Document(opts.input)
        with opts.output.open("wt") as f:
            logger.info(f"Writing output to '{opts.output}'")
            f.write(doc.render({}).prettify())
    except ProcessedException as ex:
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