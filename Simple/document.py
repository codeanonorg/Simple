"""
 Copyright (c) 2021 aq
 
 This software is released under the MIT License.
 https://opensource.org/licenses/MIT
"""

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
    is_component: bool
    name: str
    inputs: List[str]
    components: Dict[str, "Document"]

    def __init__(self, path: os.PathLike[str]) -> None:
        self.path = Path(path).resolve().absolute()
        self.cwd = self.path.parent

        with path.open("rt") as f:
            logger.debug(f"Parsing file '{path}'")
            self.html = BeautifulSoup(f, "html.parser")

        tag = next(tags(self.html.children))
        if tag is not None and tag.name == "def":
            logger.debug("Input is defining a component")
            self.is_component = True
            self.name = str(tag.attrs["name"])
            try:
                self.inputs = [s.strip() for s in self.html.attrs["props"].split(",")]
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
            component = Document(self.cwd / src)
            assert (
                component.is_component
            ), f"Included file at '{component.path}' does not define a component"
            self.components[component.name] = component

    def render(self, context: Dict[str, str]) -> BeautifulSoup:
        html = copy.deepcopy(self.html)

        for name, component in self.components.items():
            tags = html.find_all(name.lower())
            if len(tags) == 0:
                logger.warn(f"Component '{name}' is unused in document '{self.path}'")
            else:
                for tag in tags:
                    props = dict(tag.attrs)
                    for s in props.keys():
                        if s not in component.input:
                            logger.warn(
                                f"Attribute '{s}' is not used in component '{name}'"
                            )
                    child_context = {**context, **props}
                    tag.replace_with(component.render(child_context))
        if self.is_component:
            html.find("def").replace_with_children()
        return html


def tags(it: Iterator[Any]) -> Iterator[Tag]:
    return filter(lambda v: isinstance(v, Tag), it)
