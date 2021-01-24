"""
 Copyright (c) 2021 SolarLiner, jdrprod, Arxaqapi
 
 This software is released under the MIT License.
 https://opensource.org/licenses/MIT
"""

import logging
import sys
from typing import List
from pathlib import Path
from argparse import ArgumentParser
from dataclasses import dataclass


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
    return Options(args.input, args.output, logging.WARN - args.v * 10)


def create_logger(log_level: int):
    logger = logging.getLogger()
    logger.setLevel(log_level)
    logger.addHandler(logging.StreamHandler(sys.stderr))


def main(args: List[str]) -> int:
    opts = parse_args(args[1:])
    create_logger(opts.log_level)
    logger = logging.getLogger(__name__)
    logger.info(f"Options: {opts}")

    return 0