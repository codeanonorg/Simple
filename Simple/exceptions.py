"""
 Copyright (c) 2021 SolarLiner, jdrprod, Arxaqapi
 
 This software is released under the MIT License.
 https://opensource.org/licenses/MIT
"""


class ProcessedException(Exception):
    def __init__(self, exn: Exception) -> None:
        self.exn = exn