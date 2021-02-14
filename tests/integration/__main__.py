from unittest import TextTestRunner
from pathlib import Path

from . import IntegrationTestSuite

TextTestRunner().run(IntegrationTestSuite(Path(__file__).parent))