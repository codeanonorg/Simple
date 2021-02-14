"""
 Copyright (c) 2021 aq

 This software is released under the MIT License.
 https://opensource.org/licenses/MIT
"""

from .exceptions import ProcessException
from .logs import DocumentLogAdapter
import itertools
import os
import logging
import copy
from pathlib import Path
from typing import Any, Dict, Iterable, Iterator, List, Optional, Sequence, TypeVar

from .htmlparser import Node, Tag, Document as HTMLDocument, TextNode, read

logger = logging.getLogger(__name__)


class Document:
    path: Path
    cwd: Path
    adapter: DocumentLogAdapter
    parent: Optional["Document"]
    is_component: bool
    name: str
    inputs: List[str]
    components: Dict[str, "Document"]

    def __init__(
        self, path: os.PathLike[str], *, parent: Optional["Document"] = None
    ) -> None:
        self.path = Path(path).resolve().absolute()
        self.cwd = self.path.parent
        self.adapter = DocumentLogAdapter(logger, self)
        self.parent = parent

        try:
            with self.path.open("rt") as f:
                logger.info(f"Parsing file '{path}'")
                self.html = read(f)
        except IOError as ex:
            self.adapter.critical(f"Cannot parse document: {ex}")
            raise ProcessException(self, Exception(f"Cannot parse document: {ex}"))
        if self.html is None:
            raise ProcessException(self, ValueError("HTML document is incomplete"))

        root = self.html.root
        if root is None:
            raise ProcessException(self, Exception("HTML is empty"))
        if root.name == "def":
            self.adapter.debug("Input is defining a component")
            self.is_component = True
            self.name = root.attrs["name"].lower()
            try:
                self.inputs = [s.strip() for s in root.attrs["props"].split(",")]
            except KeyError:
                self.inputs = []
        else:
            self.is_component = False
            self.inputs = []
            self.name = "__root__"

        self.components = {}
        for tag in self.html.find_all("include"):
            # tag.remove()
            if "src" not in tag.attrs:
                raise ProcessException(
                    self,
                    Exception("Component include does not have a source link"),
                    extra=dict(node=tag),
                )
            src = tag.attrs["src"]
            component = Document(self.cwd / src, parent=self)
            if not component.is_component:
                raise ProcessException(
                    component,
                    Exception("Does not define a component"),
                    extra=dict(node=tag),
                )
            self.components[component.name] = component

    def render(self, context: Dict[str, str]) -> HTMLDocument:
        return HTMLDocument(
            [
                cnode
                for node in (
                    self.html.root.children if self.is_component else self.html.children
                )
                for cnode in self.inflate(node, context)
            ]
        )

    def inflate(self, node: Node, context: Dict[str, str]) -> List[Node]:
        if isinstance(node, Tag):
            if node.name in self.components:
                component = self.components[node.name]
                for s in node.attrs.keys():
                    if s not in component.inputs:
                        self.adapter.warn(f"Unknown attribute {s!r} in <{node.name}/>")
                child_context = {**context, **node.attrs}
                return component.render(child_context).children

            elif node.name == "include":
                return []
            elif node.name == "content":
                if "prop" not in node.attrs:
                    self.adapter.warn(
                        f"Content tag should have a prop attribute",
                        extra=dict(node=node),
                    )
                elif node.attrs["prop"] not in context:
                    self.adapter.warn(
                        f"Variable {node.attrs['prop']!r} not defined in context",
                        extra=dict(node=node, context=context),
                    )
                self.adapter.debug(
                    f"Replacing reference to {node.attrs['prop']!r}",
                    extra=dict(node=node),
                )
                text = context[node.attrs["prop"]]
                return [TextNode(range=node.range.start.range(text), text=text)]
            children = [n for c in node.children for n in self.inflate(c, context)]
            node = copy.deepcopy(node)
            node.children = children
            return [node]
        return [node]
