"""
 Copyright (c) 2021 SolarLiner, jdrprod, Arxaqapi
 
 This software is released under the MIT License.
 https://opensource.org/licenses/MIT
"""

import logging
from typing import List
from . import logs

log = logging.getLogger(__name__)


def main(args: List[str]) -> int:
    print("Hello, world")
    log.warning("Test ?")
    return 0
