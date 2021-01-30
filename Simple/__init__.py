"""
 Copyright (c) 2021 SolarLiner, jdrprod, Arxaqapi
 
 This software is released under the MIT License.
 https://opensource.org/licenses/MIT
"""

import logging

from typing import List
from pathlib import Path
from argparse import ArgumentParser
from dataclasses import dataclass

from Simple.document import Document
from Simple.logs import create_logger


@dataclass
class Options:
    input: Path
    output: Path
    log_level: int


def parse_args(args: List[str]) -> Options:
    parser = ArgumentParser()
    parser.add_argument("input", nargs=1, type=Path, help="Input HTML file to process")
    parser.add_argument("-o", "--output", nargs=1, type=Path, help="Output file path")
    parser.add_argument(
        "-v", action="count", default=0, help="Increase verbosity level"
    )
    args = parser.parse_args(args)
    return Options(args.input[0], args.output[0], logging.WARN - args.v * 10)


def main(args: List[str]) -> int:
    opts = parse_args(args[1:])
    logger = create_logger(opts.log_level)

    doc = Document(opts.input)
    with opts.output.open("wt") as f:
        logger.info(f"Writing output to '{opts.output}'")
        f.write(doc.render({}).prettify())

    return 0
