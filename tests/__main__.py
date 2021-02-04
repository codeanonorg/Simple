"""
 Copyright (c) 2021 SolarLiner, jdrprod, Arxaqapi
 
 This software is released under the MIT License.
 https://opensource.org/licenses/MIT
"""
from pathlib import Path
import unittest
from . import integration

if __name__ == "__main__":
    unittest.TextTestRunner().run(
        integration.IntegrationTestSuite(Path(__file__).parent / "integration")
    )
