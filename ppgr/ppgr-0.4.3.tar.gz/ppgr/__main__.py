import argparse
import sys

from .ppgr import PPGR
from .terminal import no_cursor

usage = """%(prog)s [-w N] [-t T] [-l L] [-s] [-i INPUT]"""

description = """
Python Piped GRapher -

graphing tool with support for piped data with realtime updates in terminal
"""

help_help_format = """
show help about format and exit
"""

help_format = """
format of the input data, see --help-format
"""

help_format_full = """Input is read line by line, as whitespace seperated numbers,
default mode is automatic.

a - automatic
    read two values if there are two, otherwise one
t - 1 dimensional data
    always read one value
d - 2 dimensional data
    always read two values as (x, y)
s - skip this value

examples:
t   - one 1 dimensional values on every line
t t - two 1 dimensional values on every line,
      aka. outputs two points per line
s d - skip the first value on each line,
      then read two values as (x, y) pair
d d - read two (x, y) pairs"""

help_bad_line = """
fail if input line can't be parsed
"""

help_wait = """
wait at least N milliseconds between frames,
especially useful when reading from a file and an animation is desired
"""

help_time_scale = """
add T to the value of x between data points on 1D data
(defaults to using time since the start of program as x)
"""

help_limit = """
show at most L points on the screen at the same time,
allows for a sliding window on the data
"""

help_no_animate = """
draw a static image from the input
(aka. only output the last frame of the animation)
"""

help_input = """
files to read the data from (defaults to stdin)
"""

help_bounds_description = """
instead of showing all points (default),
if bounds are defined they're respected
and only points within them are shown
"""

help_max_x = """
limit x axis to values < X
"""

help_min_x = """
limit x axis to values > X
"""

help_max_y = """
limit y axis to values < Y
"""

help_min_y = """
limit y axis to values > Y
"""


def main():
    parser = argparse.ArgumentParser(
        prog="ppgr",
        # usage=usage,
        description=description)

    parser.add_argument(
        "--help-format",
        action="store_true",
        help=help_help_format)
    parser.add_argument(
        "-f", "--format",
        nargs="+",
        default=["a"],
        choices=("a", "t", "d", "s"),
        help=help_format)
    parser.add_argument(
        "-x", "--fail-bad-line",
        action="store_true",
        help=help_bad_line)
    parser.add_argument(
        "-w", "--wait",
        type=int,
        metavar="N",
        help=help_wait)
    parser.add_argument(
        "-t", "--time-scale",
        type=float,
        metavar="T",
        help=help_time_scale)
    parser.add_argument(
        "-l", "--limit",
        type=int,
        metavar="L",
        help=help_limit)
    parser.add_argument(
        "-s", "--no-animate",
        action="store_true",
        help=help_no_animate)
    parser.add_argument(
        "input",
        nargs="*",
        type=argparse.FileType("r"),
        default=[sys.stdin],
        help=help_input)

    bounds = parser.add_argument_group(
        "bounds",
        help_bounds_description)
    bounds.add_argument(
        "--max-x",
        type=float,
        metavar="X",
        help=help_max_x)
    bounds.add_argument(
        "--min-x",
        type=float,
        metavar="X",
        help=help_min_x)
    bounds.add_argument(
        "--max-y",
        type=float,
        metavar="Y",
        help=help_max_y)
    bounds.add_argument(
        "--min-y",
        type=float,
        metavar="Y",
        help=help_min_y)

    argv = parser.parse_args()

    if argv.help_format:
        print(help_format_full)
        return

    ppgr = PPGR(
        argv.format,
        argv.fail_bad_line,
        argv.wait,
        argv.time_scale,
        argv.limit)

    try:
        with no_cursor():
            for f in argv.input:
                for line in f:
                    ppgr.line(line)
                    if argv.no_animate:
                        continue
                    ppgr.show(argv.max_x, argv.min_x, argv.max_y, argv.min_y)
    except KeyboardInterrupt:
        pass
    finally:
        ppgr.show(argv.max_x, argv.min_x, argv.max_y, argv.min_y, True, newline=True)


if __name__ == "__main__":
    main()
