"""
 Copyright (c) 2021 SolarLiner, jdrprod, Arxaqapi
 
 This software is released under the MIT License.
 https://opensource.org/licenses/MIT
"""

from dataclasses import dataclass
import os
from typing import *


class HTML:
    def __html__(self) -> str:
        raise NotImplementedError()


def html(node: HTML) -> str:
    return node.__html__()


@dataclass()
class Position:
    line: int
    col: int

    def range(self, text: str) -> "Range":
        if "\n" in text:
            lines = 1 + sum(1 for _ in filter(lambda c: c == "\n", text))
            new_col = text[::-1].index("\n")
            return Range(start=self, end=Position(self.line + lines, new_col))
        else:
            return Range(start=self, end=Position(self.line, self.col + len(text)))

    def __str__(self) -> str:
        return f"{self.line}:{self.col}"


@dataclass()
class Range:
    start: Position
    end: Position

    def __str__(self) -> str:
        return f"{self.start}-{self.end}"
