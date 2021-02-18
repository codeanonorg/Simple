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

from . import HTML, Position, Range, html
from .tags import Node, Comment, TextNode, Tag

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
    def document(self) -> Document:
        if not self.complete:
            from .exceptions import DocumentException

            raise DocumentException(
                "Document is not complete",
                "You are probably missing a closing tag",
                self._tag_stack_top(),
            )
        return Document(self.children)

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


def parse(text: str) -> Optional[Document]:
    from .document import DocumentParser

    p = DocumentParser(text)
    return p.document


def read(f: Union[os.PathLike, TextIO]) -> Optional[Document]:
    from .document import DocumentParser

    if hasattr(f, "read"):  # Is file object
        p = DocumentParser()
        while chunk := f.read(512):
            p.feed(chunk)
        return p.document
    else:
        from pathlib import Path

        with Path(f).open("rt") as fp:
            return read(fp)