"""
 Copyright (c) 2021 SolarLiner, jdrprod, Arxaqapi
 
 This software is released under the MIT License.
 https://opensource.org/licenses/MIT
"""
from dataclasses import dataclass, field
from typing import *
import itertools as itt

from . import HTML, Position, Range, html


@dataclass()
class Node(HTML, Iterable["Node"]):
    range: Range = field(repr=False)
    text: Optional[str]
    parent: Optional["Tag"] = field(init=False, repr=False, default=None)

    def replace_with_all(self, nodes: Sequence["Node"]) -> None:
        if self.parent is None:
            return
        ix = self.parent.children.index(self)
        self.parent.children = (
            self.parent.children[:ix] + nodes + self.parent.children[ix:]
        )

    def __str__(self):
        return f"[{self.__class__.__name__} len={len(self.text)}]"

    def __html__(self):
        return self.text

    def __iter__(self) -> Iterator["Node"]:
        yield self


class TextNode(Node):
    @staticmethod
    def fuse(nodes: Iterable["TextNode"], startpos=Position(0, 0)) -> "TextNode":
        if len(nodes) == 0:
            return TextNode(range=Range(start=startpos, end=startpos), text="")
        else:
            start = next((t.range.start for t in nodes))
            text = "".join((t.text or "" for t in nodes))
            return TextNode(range=start.range(text), text=text)


class Comment(Node):
    def __init__(self, range: Range, data: str):
        super().__init__(range=range, text=data)

    def __html__(self):
        return f"<!-- {self.text} -->"


@dataclass()
class Tag(Node):
    name: str
    attrs: Dict[str, str]
    children: List[Node] = field(default_factory=list, repr=False)
    self_closing: bool = field(default=False, repr=False)

    @property
    def inner_html(self) -> str:
        return "".join(map(html, self.children))

    def inner_tags(self) -> Iterable["Tag"]:
        return filter(lambda s: isinstance(s, Tag), self)

    def add_child(self, node: "Node"):
        node.parent = self
        self.children.append(node)

    def find_all(self, tag: str) -> Iterable["Tag"]:
        return filter(lambda s: s.name == tag, self.inner_tags())

    def find(self, tag: str) -> Optional["Tag"]:
        return next(self.find_all(tag))

    def remove(self) -> "Tag":
        if self.parent is not None:
            self.parent.children.remove(self)
        return self

    def replace_with_children(self) -> None:
        self.replace_with_all(self.children)

    def consolidate_children(self) -> None:
        def do_one(
            t: Union[
                Tuple[Literal[False], Iterator[Node]],
                Tuple[Literal[True], Iterator[TextNode]],
            ]
        ):
            if t[0]:
                return [TextNode.fuse(list(t[1]))]
            else:
                return list(t[1])

        self.children = list(
            itt.chain(
                *map(
                    do_one,
                    itt.groupby(
                        self.children, key=lambda node: isinstance(node, TextNode)
                    ),
                )
            )
        )

    def __iter__(self) -> Iterator["Node"]:
        yield self
        for child in itt.chain(*map(iter, self.children)):
            yield child

    def __str__(self):
        if self.self_closing:
            return self.text
        else:
            return f"{self.text}{''.join(map(str, self.children))}</{self.name}>"

    def __html__(self):
        if self.self_closing:
            return self.text
        else:
            return f"{self.text}{self.inner_html}</{self.name}>"
