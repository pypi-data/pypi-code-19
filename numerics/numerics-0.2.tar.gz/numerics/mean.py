#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
compute mean of data
"""

# imports
import sys
from .filters import mean
from .reduce import ReduceParser


__all__ = ['main']


def main(args=sys.argv[1:]):
    """CLI"""
    ReduceParser(mean, description=__doc__)(*args)


if __name__ == '__main__':
    main()


