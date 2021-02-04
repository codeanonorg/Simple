"""
 Copyright (c) 2021 aq
 
 This software is released under the MIT License.
 https://opensource.org/licenses/MIT
"""

from .exceptions import ProcessedException
from .logs import DocumentLogAdapter
import os
import logging
import copy
from pathlib import Path
from typing import Any, Dict, Iterable, Iterator, List, Optional, TypeVar
from bs4 import BeautifulSoup, Tag

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
        self, path: os.PathLike[str], parent: Optional["Document"] = None
    ) -> None:
        self.path = Path(path).resolve().absolute()
        self.cwd = self.path.parent
        self.adapter = DocumentLogAdapter(logger, self)
        self.parent = parent

        try:
        with path.open("rt") as f:
            logger.debug(f"Parsing file '{path}'")
            self.html = BeautifulSoup(f, "html.parser")
        except IOError as ex:
            self.adapter.critical(f"Cannot parse document: {ex}")
            raise ProcessedException(ex)

        tag = next(tags(self.html.children))
        if tag is not None and tag.name == "def":
            self.adapter.debug("Input is defining a component")
            self.is_component = True
            self.name = str(tag.attrs["name"])
            try:
                self.inputs = [s.strip() for s in tag.attrs["props"].split(",")]
            except KeyError:
                self.inputs = []
        else:
            self.is_component = False
            self.inputs = []
            self.name = "__root__"

        self.components = {}
        for tag in self.html.find_all("include"):
            tag.extract()
            src = tag.attrs["src"]
            component = Document(self.cwd / src, parent=self)
            if not component.is_component:
                component.adapter.critical("Does not define a component")
                raise ProcessedException(None)
            self.components[component.name] = component

    def render(
        self, context: Dict[str, str], children: Iterable[Tag] = []
    ) -> BeautifulSoup:
        # Getting a working copy of the structure
        html = copy.deepcopy(self.html)

        self._replace_props(html, context)
        self._replace_children(html, children)
        self._replace_components(html, context)

        # removing the "def" part
        if self.is_component:
            html.find("def").replace_with_children()

        return html

    def _replace_components(self, html: BeautifulSoup, context: Dict[str, str]):
        for name, component in self.components.items():
            tags = html.find_all(name.lower())
            if len(tags) == 0:
                self.adapter.warn(f"<{name} /> is unused")
            else:
                for tag in tags:
                    props = dict(tag.attrs)
                    for s in props.keys():
                        if s not in component.inputs:
                            self.adapter.warn(f"Unknown attribute '{s}' in <{name} />")
                    child_context = {**context, **props}
                    tag.replace_with(component.render(child_context, tag.children))

    def _replace_children(self, html: BeautifulSoup, children: Iterable[Tag]):
        if (placeholder := html.find("children")) is not None:
            placeholder.replace_with(children)

    def _replace_props(self, html: BeautifulSoup, context: Dict[str, str]):
        for c in html.find_all("content"):
            if "prop" not in c.attrs:
                self.adapter.warn(f"Content tag should have a 'prop' attribute")
                if c.remove is not None:
                    c.remove()
            elif c.attrs["prop"] not in context:
                self.adapter.warn(
                    f"Variable '{c.attrs['prop']}' not defined in context"
                )
                if c.remove is not None:
                    c.remove()
            else:
                self.adapter.debug(f"Replacing reference to {c.attrs['prop']}")
                c.replace_with(context[c.attrs["prop"]])


def tags(it: Iterator[Any]) -> Iterator[Tag]:
    return filter(lambda v: isinstance(v, Tag), it)
