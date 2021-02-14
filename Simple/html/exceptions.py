"""
 Copyright (c) 2021 SolarLiner, jdrprod, Arxaqapi
 
 This software is released under the MIT License.
 https://opensource.org/licenses/MIT
"""

from typing import Optional
from . import Range


class DocumentException(Exception):
    def __init__(self, msg: str, range: Optional[Range] = None) -> None:
        super().__init__(f"{range}: {msg}")
        self.range = range