"""
.. module:: test_stratify
   :synopsis: Unit tests for stratify module
"""

import pytest

from nutsflow import Collect, Sort
from nutsflow.common import StableRandom
from nutsml import Stratify


def test_Stratify():
    samples = [('pos', 1), ('pos', 1), ('neg', 0)]
    stratify = Stratify(1, mode='up', rand=StableRandom(0))
    stratified = samples >> stratify >> Sort()
    assert stratified == [('neg', 0), ('neg', 0), ('pos', 1), ('pos', 1)]

    samples = [('pos', 1), ('pos', 1), ('pos', 1), ('neg1', 0), ('neg2', 0)]
    stratify = Stratify(1, mode='downrnd', rand=StableRandom(0))
    stratified = samples >> stratify >> Sort()
    assert stratified == [('neg1', 0), ('neg2', 0), ('pos', 1), ('pos', 1)]

    with pytest.raises(ValueError) as ex:
        samples >> Stratify(1, mode='invalid') >> Collect()
    assert str(ex.value).startswith('Unknown mode')



