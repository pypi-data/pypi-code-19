"""
.. module:: stratify
   :synopsis: Stratification of sample sets
"""
from __future__ import absolute_import

import random as rnd

from nutsflow import nut_processor, Sort
from .datautil import upsample, random_downsample


@nut_processor
def Stratify(iterable, labelcol, mode='downrnd', rand=rnd.Random()):
    """
    iterable >> Stratify(labelcol, mode='downrnd', rand=rnd.Random())

    Stratifies samples by either randomly down-sampling classes or
    up-sampling classes by duplicating samples.
    Loads all samples in memory!

    >>> from nutsflow import Collect
    >>> samples = [('pos', 1), ('pos', 1), ('neg', 0)]
    >>> samples >> Stratify(1) >> Sort()
    [('neg', 0), ('pos', 1)]

    :param iterable over tuples iterable: Iterable of tuples where column
       labelcol contains a sample label that is used for stratification
    :param int labelcol: Column of tuple/samples that contains the label
    :param string mode:
       'downrnd' : randomly down-sample
       'up' : up-sample
    :param rand.Random rand: Random number generator used for down-sampling
    :return: Stratified samples
    :rtype: Iterator over tuples
    """
    samples = list(iterable)
    if mode == 'up':
        stratified = upsample(samples, labelcol, rand)
    elif mode == 'downrnd':
        stratified = random_downsample(samples, labelcol, rand)
    else:
        raise ValueError('Unknown mode: ' + mode)
    return iter(stratified)


