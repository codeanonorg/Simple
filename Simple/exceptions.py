"""
 Copyright (c) 2021 SolarLiner, jdrprod, Arxaqapi

 This software is released under the MIT License.
 https://opensource.org/licenses/MIT
"""
from typing import Optional
import Simple


class ProcessException(Exception):
    def __init__(
        self,
        doc: "Simple.document.Document",
        exn: Exception,
        extra: Optional[dict] = None,
    ) -> None:
        self.doc = doc
        self.exn = exn
        self.extra = extra or {}

    def __str__(self) -> str:
        return f"{self.doc.path}: {self.exn}"
