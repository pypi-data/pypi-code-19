"""
naposapi
~~~~~~~~
A requests based API to lookup porphyrinogenic classifications of drugs on the NAPOS database,
hosted on (www.drugs-porphyria.org).
"""

from collections import namedtuple
from enum import Enum

import requests
from lxml import html


BASE_URL = 'http://www.drugs-porphyria.org/languages/UnitedKingdom/'


class Classification(Enum):
    """
    Describes the different levels of classification, whether or not a given drug is known to be
    porphyrinogenic.

    Taken from e.g. http://www.drugs-porphyria.org/languages/UnitedKingdom/s1.php
    """
    NP = (
        0,
        'Not porphyrinogenic',
        'Used as a first hand choice. No precautions needed.'
    )
    PNP = (
        1,
        'Probably not porphyrinogenic',
        'Used as a first hand choice. No precautions needed.'
    )
    PSP = (
        2,
        'Possibly porphyrinogenic',
        'Only used when no safer alternative is available. '
        'Precautions motivated in vulnerable patients.'
    )
    PRP = (
        3,
        'Probably porphyrinogenic',
        'Prescribed only on strong or urgent indications. '
        'Precautions motivated in all patients.'
    )
    P = (
        4,
        'Porphyrinogenic',
        'Prescribed only on urgent indications. Precautions taken in all patients.'
    )
    NC = (
        -1,
        'Not yet classified',
        'Not yet safety classified and should therefore not be used. '
        'Prescribed only on strong indication when no safer alternative is available. '
        'Seek advice from a porphyria specialist.'
    )


class ClassificationResult(namedtuple('ClassificationResult', ['code', 'level', 'name', 'description'])):
    """
    Represents a classification for a given ATC code.
    """
    @classmethod
    def from_code(cls, code):
        level, name, description = Classification[code].value
        return cls(code, level, name, description)


class ParserError(Exception):
    pass


def lookup_classification(atc_code):
    """
    For a given ATC code, return the porphyrinogenic classification from the NAPOS database.
    """
    response = requests.get(BASE_URL + 's3.php?atc_code=' + atc_code)
    tree = html.fromstring(response.content)
    rows = tree.cssselect('table.ramme tr.sramme')[1:]
    if len(rows) != 1:
        raise ParserError('Got more than one result row for classification of %s' % atc_code)

    row = rows[0]
    if len(row) != 6:
        raise ParserError('Expect 6 columns per row, got %s' % len(row))

    code = row[3].text_content().strip()
    return ClassificationResult.from_code(code)
