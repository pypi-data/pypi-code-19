#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
cleans up outliers
"""

# imports
import argparse
import os
import sys
import time
from .manipulate import ManipulationParser

# module globals
__all__ = ['main', 'CleanseParser']


class CleanseParser(ManipulationParser):
    """CLI option parser"""
    def __init__(self, **kwargs):
        ManipulationParser.__init__(self, **kwargs)


def main(args=sys.argv[1:]):
    """CLI"""

    # parse command line options
    parser = CleanseParser()
    options = parser.parse_args(args)

    # write manipulated data
    parser.write(parser.process())

if __name__ == '__main__':
    main()


