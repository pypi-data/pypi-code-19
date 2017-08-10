"""Control code revealer.

Usage: ccr FILE PROG [ARG]...

Run a program with arguments and pretend to be a terminal, teeing output
to a file.

This can be used to debug what control codes a troublesome program is
emitting when it thinks it's talking to a terminal.
"""

import argparse
import os
import pty
import sys


def main(args):
    parser = argparse.ArgumentParser()
    parser.add_argument('file')
    parser.add_argument('argv', nargs=argparse.REMAINDER)
    args = parser.parse_args(args)
    with open(args.file, 'wb') as f:
        return pty.spawn(args.argv, _reader(f))


def _reader(file):
    def read_escape_cc(fd):
        """Read from a file descriptor and echo to file."""
        output = os.read(fd, 1024)
        file.write(output)
        return output
    return read_escape_cc


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
