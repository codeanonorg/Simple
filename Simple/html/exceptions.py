"""
 Copyright (c) 2021 SolarLiner, jdrprod, Arxaqapi
 
 This software is released under the MIT License.
 https://opensource.org/licenses/MIT
"""

from Simple.html import Range, html
from Simple.html.tags import Node
from typing import Optional


class DocumentException(Exception):
    def __init__(
        self,
        msg: str,
        hint: Optional[str] = None,
        node: Optional[Node] = None,
        default_range: Optional[Range] = None,
    ) -> None:
        self.node = node
        self.hint = hint
        if node:
            self.range = node.range
        else:
            self.range = default_range
        super().__init__(msg)

    def __str__(self) -> str:
        if self.node:
            node_html = html(self.node)
            node_first_line = node_html[: node_html.index("\n")]
            line_display = f"{self.range.start.line} |"
            cont_display = "|".rjust(len(line_display), " ")
            if self.hint:
                return f"{super().__str__()}\n{line_display} {node_first_line}\n{cont_display} ...\n\t\033[36mhint\033[0m: {self.hint}"
            else:
                return f"{super().__str__()}\n{line_display} {node_first_line}\n{cont_display} ..."
        elif self.range:
            return f"{self.range}: {super().__init__()}"
        else:
            return super().__init__()
