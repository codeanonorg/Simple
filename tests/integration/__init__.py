"""
 Copyright (c) 2021 SolarLiner, jdrprod, Arxaqapi
 
 This software is released under the MIT License.
 https://opensource.org/licenses/MIT
"""

import os
import json
import unittest
from pathlib import Path

from Simple.document import Document


class FolderExpansionTest(unittest.TestCase):
    def __init__(self, cwd: Path) -> None:
        super().__init__(methodName="test_matches_snapshot")
        self.path = cwd

    def test_matches_snapshot(self):
        input = Document(self.path / "index.html")
        expected = Document(self.path / "expected.html")
        if (data_path := self.path / "data.json").exists():
            with data_path.open("rt") as d:
                data = json.load(d)
        else:
            data = {}
        self.assertEqual(
            input.render(data).prettify(), expected.html.prettify(), str(self.path)
        )


class IntegrationTestSuite(unittest.TestSuite):
    def __init__(self, cwd: Path) -> None:
        tests = list(
            map(
                FolderExpansionTest,
                filter(
                    lambda p: p.is_dir() and not p.name.startswith("__"),
                    map(lambda s: cwd / s, os.listdir(cwd)),
                ),
            )
        )
        super().__init__(tests=tests)
