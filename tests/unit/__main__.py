import unittest
from pathlib import Path


loader = unittest.TestLoader()
suite = loader.discover(str(Path(__file__).parent))
runner = unittest.TextTestRunner().run(suite)