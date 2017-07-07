from rigor.model import Suite, Method, Namespace, Validator, State
from collections import OrderedDict

import pytest
import os
import related
import json


def test_execute():
    directories = ["/Users/ianmaurer/code/knowledge/qa/api/therapies"]
    suite = Suite(directories=directories, tags_excluded=["broken"])
    success = suite.execute()
    assert success
    assert len(suite.passed) == 1
