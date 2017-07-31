from __future__ import absolute_import, division, print_function

import os.path as op
from ...core import MvpWithin
from ... import testdata_path
from ..selectors import fisher_criterion_score
import pytest
import os
import random
from glob import glob

testfeats = [op.join(testdata_path, 'run1.feat'),
             op.join(testdata_path, 'run2.feat')]

mvp_within = MvpWithin(source=testfeats, read_labels=True,
                       remove_contrast=[], invert_selection=False,
                       ref_space='epi', statistic='cope', remove_zeros=False,
                       mask=None)

mvp_within.create()

@pytest.mark.selector
def test_fisher_criterion_score():

    scores = fisher_criterion_score(mvp_within.X, mvp_within.y)
    assert(scores.shape[0] == mvp_within.X.shape[1])