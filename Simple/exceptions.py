"""
 Copyright (c) 2021 SolarLiner, jdrprod, Arxaqapi

 This software is released under the MIT License.
 https://opensource.org/licenses/MIT
"""


class ProcessException(Exception):
    def __init__(self, doc: "Simple.document.Document", exn: Exception) -> None:
        self.doc = doc
        self.exn = exn

    def __str__(self) -> str:
        return f"{self.doc.path}: {self.exn}"
