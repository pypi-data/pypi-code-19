"""
Test utility functions.
"""

from __future__ import print_function

from ditz import util
from ditz import term


def test_match():
    "Test issue name match function"

    names = """
    my-comp-1 my-comp-2 his-comp-1 fred-23 brian-33 p45-42
    my-othercomp-1
    """.split()

    tests = (("my", 3), ("his", 1), ("x", 0), ("1", 3), ("3", 0),
             ("23", 1), ("b33", 1), ("hc1", 1), ("p45", 1), ("p442", 1),
             ("myo", 1))

    for text, count in tests:
        matches = list(util.matching_issue_names(text, names))
        assert len(matches) == count, "%s: expected %d matches, got %d" \
               % (text, count, len(matches))


def test_func():
    "Test utility functions"

    for num in 0.43, 1, 23, 64, 432, 3656, 1539424, 41749360, 97492847:
        print(num, '=', util.timespan(num))

    print()
    print(util.extract_username('Alan Partridge <alan@norwichradio.co.uk>'))

    print()
    names = "fred brian derek tarquin ermintrude cyril"
    util.print_columns(names.split(), linelen=45)

    print()
    print(util.default_name())
    print(util.default_email())

    print(util.hostname())
    print(util.editor())


def test_term():
    "Test terminal functions"

    print(term.get_terminal_size())


if __name__ == "__main__":
    test_match()
    test_func()
    test_term()
