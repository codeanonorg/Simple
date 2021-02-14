from dataclasses import dataclass, field
import abc
import itertools as itt
import logging

from html.parser import HTMLParser
import os
from typing import (
    Any,
    Dict,
    Iterable,
    Iterator,
    List,
    Literal,
    Optional,
    Sequence,
    TextIO,
    Tuple,
    TypeVar,
    Union,
)

logger = logging.getLogger(__name__)

K, V = tuple(map(TypeVar, ["K", "V"]))
AssocList = List[Tuple[K, V]]

# From https://html.spec.whatwg.org/multipage/syntax.html#void-elements
SELF_CLOSING_TAGS = [
    "area",
    "base",
    "br",
    "col",
    "embed",
    "hr",
    "img",
    "input",
    "link",
    "meta",
    "param",
    "source",
    "track",
    "wbr",
]


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


@dataclass()
class Range:
    start: Position
    end: Position


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


@dataclass()
class Document(HTML, Iterable[Node]):
    children: List[Node]

    def roots(self) -> List[Tag]:
        return list(filter(lambda s: isinstance(s, Tag), self.children))

    @property
    def root(self) -> Optional[Tag]:
        roots = self.roots()
        if len(roots) > 0:
            return roots[0]
        else:
            return None

    def find_all(self, tag: str) -> Iterable[Tag]:
        return itt.chain(*(t.find_all(tag) for t in self.roots()))

    def find(self, tag: str) -> Optional[Tag]:
        return next(self.find_all(tag))

    def __iter__(self) -> Iterator[Node]:
        return itt.chain(*map(iter, self.children))

    def __html__(self) -> str:
        return "".join(map(html, self.children))


class DocumentParser(HTMLParser):
    children: List[Node]
    _tag_stack: List[Tag]

    def __init__(self, data: Optional[str] = None):
        super().__init__(convert_charrefs=True)
        self.reset()

        if data is not None:
            self.feed(data)

    @property
    def complete(self):
        return len(self._tag_stack) == 0

    @property
    def document(self) -> Optional[Document]:
        if self.complete:
            return Document(self.children)
        return None

    def handle_starttag(self, tag: str, attrs: AssocList[str, str]):
        if tag in SELF_CLOSING_TAGS:
            self.handle_startendtag(tag, attrs)
        else:
            text = self.get_starttag_text()
            child = Tag(
                name=tag, attrs=dict(attrs), text=text, range=self.getpos().range(text)
            )
            self._push_node(child)

    def handle_endtag(self, tag: str):
        node = self._tag_stack.pop()
        node.range.end = self.getpos()
        node.consolidate_children()

    def handle_startendtag(self, tag: str, attrs: AssocList[str, str]) -> None:
        text = self.get_starttag_text()
        node = Tag(
            name=tag,
            attrs=dict(attrs),
            text=text,
            range=self.getpos().range(text),
            self_closing=True,
        )
        self._push_node(node, skip_stack=True)

    def handle_data(self, data: str) -> None:
        self._push_node(TextNode(range=self.getpos().range(data), text=data))

    def handle_comment(self, data: str) -> None:
        if (parent := self._tag_stack_top()) is not None:
            parent.add_child(Comment(range=self.getpos().range(data), data=data))
        else:
            self.children.append(Comment(range=self.getpos().range(data), data=data))

    def getpos(self) -> Position:
        l, c = super().getpos()
        return Position(l, c)

    def flush(self) -> None:
        if len(self._tag_stack) > 0:
            self.children.append(self._tag_stack[0])
        self._tag_stack = []

    def reset(self) -> None:
        super().reset()
        self.children = []
        self._tag_stack = []

    def _tag_stack_top(self) -> Optional[Tag]:
        if len(self._tag_stack) > 0:
            return self._tag_stack[-1]

    def _push_node(self, node: Node, *, skip_stack: bool = False):
        if len(self._tag_stack) == 0:
            self.children.append(node)
        if (parent := self._tag_stack_top()) is not None:
            if isinstance(parent, Tag):
                parent.add_child(node)
            else:
                self._tag_stack.pop()
                self._push_node(node)
        if isinstance(node, Tag) and not skip_stack:
            self._tag_stack.append(node)


def parse(text: str) -> Document:
    p = DocumentParser(text)
    p.flush()
    return p.document


def read(f: Union[os.PathLike, TextIO]) -> Document:
    if hasattr(f, "read"):  # Is file object
        p = DocumentParser()
        while chunk := f.read(512):
            p.feed(chunk)
        p.flush()
        return p.document
    else:
        from pathlib import Path

        with Path(f).open("rt") as fp:
            return read(fp)
