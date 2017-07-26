import os
import itab
import logging

from intervaltree import IntervalTree
from tqdm import tqdm
from collections import defaultdict

from bgparsers.readers.common import __count_lines

ELEMENTS_HEADER = ['CHROMOSOME', 'START', 'STOP', 'STRAND', 'ELEMENT', 'SEGMENT', 'SYMBOL']
"""
Headers of the data expected in the elements file (see :class:`~oncodrivefml.main.OncodriveFML`).
"""

ELEMENTS_SCHEMA = {
    'fields': {
        'CHROMOSOME': {'reader': 'str(x)', 'validator': "x in ([str(c) for c in range(1,23)] + ['X', 'Y', 'M'])"},
        'START': {'reader': 'int(x)', 'validator': 'x > 0'},
        'STOP': {'reader': 'int(x)', 'validator': 'x > 0'},
        'STRAND': {'reader': 'str(x)', 'validator': "x in ['.', '+', '-']"},
        'ELEMENT': {'reader': 'str(x)'},
        'SEGMENT': {'reader': 'str(x)', 'nullable': 'True'},
        'SYMBOL': {'reader': 'str(x)', 'nullable': 'True'}
}}


def elements(file, show_progress=True):
    """
    Parse an elements file compliant with :attr:`ELEMENTS_HEADER`

    Args:
        file: elements file. If 'SEGMENT' field is not present, the value of the 'ELEMENT'
            is used instead.

    Returns:
        dict: elements' (see :ref:`elements <elements dict>`).

    """

    lines_count = __count_lines(file) if show_progress else None

    elements = {}
    with itab.DictReader(file, header=ELEMENTS_HEADER, schema=ELEMENTS_SCHEMA) as reader:
        all_errors = []
        msg = "'{}'".format(os.path.basename(file)) if type(file) == str else ""
        for i, (r, errors) in enumerate(tqdm(reader, total=lines_count, desc="Parsing elements {}".format(msg).rjust(40), disable=(not show_progress)), start=1):
            # Report errors and continue
            if len(errors) > 0:
                all_errors += errors
                continue

            r['LINE'] = i

            elements[r['ELEMENT']] = elements.get(r['ELEMENT'], []) + [r]

        if len(all_errors) > 0:
            logging.warning("There are {} errors at {}. {}".format(
                len(all_errors), os.path.basename(file),
                " I show you only the ten first errors." if len(all_errors) > 10 else ""
            ))
            for e in all_errors[:10]:
                logging.warning(e)

    return elements


def elements_tree(file):
    e = elements(file)
    regions_tree = defaultdict(IntervalTree)
    for i, (k, allr) in enumerate(tqdm(e.items(), total=len(e), desc="Building mapping tree".rjust(40))):
        for r in allr:
            regions_tree[r['CHROMOSOME']][r['START']:(r['STOP']+1)] = (r['ELEMENT'], r['LINE'])
    return regions_tree

