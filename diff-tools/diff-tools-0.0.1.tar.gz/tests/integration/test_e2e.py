import os
import json

from diff.tools.models import DiffTask

import pytest

from . import TEST_DATA_DIR


@pytest.mark.xfail(run=False)
def test(test_case, keys):
    dir = os.path.join(TEST_DATA_DIR, test_case)
    base_file_name = os.path.join(dir, 'base.csv')
    reg_file_name = os.path.join(dir, 'reg.csv')
    task = DiffTask(base_file_name=base_file_name,
                    reg_file_name=reg_file_name,
                    key_list=keys)
    task.compute()
    result = task.summary()
    print result
    expected = open(os.path.join(dir, 'result.json')).read()
    expected = json.loads(expected)
    assert expected['differences'] == result['differences']


def test_0():
    # No difference
    test("0", ["policyID"])


def test_1():
    # Missing row in reg
    test("1", ["policyID"])


def test_2():
    # Column data differences in reg
    test("2", ["policyID"])


def test_3():
    # Missing row in reg
    test("3", ["policyID", "statecode", "county"])


def test_4():
    # Missing column in reg
    test("4", ["policyID"])


def test_5():
    # Duplicated key
    test("5", ["policyID"])
