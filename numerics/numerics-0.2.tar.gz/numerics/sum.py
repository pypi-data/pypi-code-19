#!/usr/bin/env python

"""
sum columns in CSV
"""

import sys
from .reduce import ReduceParser

def main(args=sys.argv[1:]):
    """CLI"""

    ReduceParser(sum, description=__doc__)(*args)

if __name__ == '__main__':
    main()
