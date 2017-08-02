#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
estimate Gaussian parameters for a given distribution of numbers

"""


import argparse
import os
import sys
from .filters import mean

def gaussian(data):
    """
    find mean + variance; fit to a Gaussian distribution
    """

    # find mean
    _mean = mean(data)

    # find variance
    sigma_squared = sum([(x-_mean)**2
                         for x in data])/float(len(data))

    # return parameters
    return (_mean, sigma_squared)


def main(args=sys.argv[1:]):

    raise NotImplementedError('TODO')

    # parse command line
    parser = argparse.ArgumentParser(description=__doc__)
    options = parser.parse_args(args)

if __name__ == '__main__':
    main()
