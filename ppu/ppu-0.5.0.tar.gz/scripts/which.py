#! /usr/bin/env python

import sys
from ppu.find_executable import find_executable

if len(sys.argv) != 2:
    sys.exit("Usage: %s program" % sys.argv[0])

program = find_executable(sys.argv[1])
if program:
    print(program)
