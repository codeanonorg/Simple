"""
 Copyright (c) 2021 SolarLiner, jdrprod, Arxaqapi

 This software is released under the MIT License.
 https://opensource.org/licenses/MIT
"""


from typing import Optional


class ProcessedException(Exception):
    def __init__(self, exn: Optional[Exception]) -> None:
        self.exn = exn
