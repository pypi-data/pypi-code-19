import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir)))

import pytest
import numpy as np

from chroma import conversions


@pytest.mark.parametrize("rgb,lab", [
    ((12, 34, 56), (12.65624852526134, 0.12256520883417721, -16.833209795877284))
])
def test_rgb2lab(rgb, lab):
    assert np.allclose(conversions.rgb2lab(rgb), lab, atol=1e-4)


@pytest.mark.parametrize("lab,rgb", [
    ((12.65624852526134, 0.12256520883417721, -16.833209795877284), (12, 34, 56))
])
def test_lab2rgb(lab, rgb):
    assert all([a == b for a, b in zip(conversions.lab2rgb(lab), rgb)])
