import pytest

import os
from glob import glob
import pickle
import time

from basis import (CharacterContainer, CasedCharContainer,
                   UncasedCharContainer, WordContainer)

CHARACTERS = [CasedCharContainer, UncasedCharContainer]
WORDS = [WordContainer]


def test_character_contanier_length():
    for klass in CHARACTERS:
        ch = klass()
        assert len('the dog at the park.') == \
            len(ch.transform('the dog at the park.'))


def test_character_inverse_transform():
    text = ('Hello, my name is Joe! '
            'The quick, browm fox jumped over the lazy dog.')

    ch = CasedCharContainer()

    assert text == ''.join(ch.inverse_transform(ch.transform(text)))

    uch = UncasedCharContainer()

    assert text.lower() == ''.join(uch.inverse_transform(uch.transform(text)))


def test_character_padding_inverse_transform():
    ch_padded = CasedCharContainer(padded=True)
    ch_unpadded = CasedCharContainer(padded=False)

    texts = ['Hello, my name is Joe!',
             'The quick, browm fox jumped over the lazy dog.']

    p1, p2 = ch_padded.transform(texts)
    u1, u2 = ch_unpadded.transform(texts)

    assert len(p1) == len(u1)
    assert len(p2) == len(u2)

    assert (np.array(u1) + 1) == np.array(p1)


def test_character_save_load():
    text = 'Hello, my name is Joe!'

    for klass in CHARACTERS:
        for padded in [True, False]:
            ch = klass(padded=padded)
            t = ch.transform(text)
            ch.save('/tmp/saveloadtest')
            och = CasedCharContainer.load('/tmp/saveloadtest')

            assert t == och.transform(text)
