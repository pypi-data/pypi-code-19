from __future__ import print_function
import pytest
import os, sys
import numpy as np

sys.path.insert(0, os.path.abspath('../../..'))
from hublib import ureg, Q_
from hublib.rappture import conv_rap, conv_pint, rap_unit

class TestUnits:

    def test_1(self):
        print(conv_rap("10m"))

    def test_2(self):
        print(conv_rap("300W/m**2*K"))

    def test_3(self):
        print(conv_rap("300W/m**2*C", "W/m**2*C"))





