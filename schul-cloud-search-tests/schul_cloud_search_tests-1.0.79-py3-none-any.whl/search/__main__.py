"""
Run the tests agains a search engine.
"""

import os
import sys
import pytest

HERE = os.path.dirname(__file__)
API_TESTS = HERE
arguments = sys.argv[1:]
if len(arguments) > 0 and not arguments[0].startswith("-"):
    arguments.insert(0, "--url")

errcode = pytest.main([API_TESTS] + arguments)
sys.exit(errcode)
