# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function

import StringIO

import pytest
import numpy as np
from numpy.testing import assert_array_equal


def test_initialize():
    dic = {
    "main/accuracy": 0.997883335351944,
    "None/predictor/l1/b/grad/percentile/4": 0.00039319694746007487,
    "elapsed_time": 291.5265939235687,
    "epoch": 20,
    }