#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" 
file: character_container.py
description: easy utilities for mapping things to character vectors
author: Luke de Oliveira (lukedeo@vaitech.io)

Copyright 2017 Vai Technologies, LLC. All Rights Reserved.
"""


import string
import numpy as np
import six

from .token_container import TokenContainer, PAD_TOKEN


class CharacterContainer(TokenContainer):
    """docstring for CharacterContainer"""

    def __init__(self, character_set=None, padded=True):
        if character_set is None:
            character_set = (string.digits + string.punctuation +
                             string.ascii_lowercase +
                             string.ascii_uppercase + ' ')
        super(CharacterContainer, self).__init__(
            vocabulary=list(character_set),
            padded=padded
        )
        self._character_set = character_set

    @property
    def character_set(self):
        return self._character_set

    def _process_iter(self, text_iter, **kwargs):
        return map(list, text_iter)

    def _process_singleton(self, text, **kwargs):
        return list(text)


class CasedCharContainer(CharacterContainer):
    """docstring for CharacterContainer"""

    def __init__(self, padded=True):
        super(CasedCharContainer, self).__init__(
            character_set=None,
            padded=padded
        )


class UncasedCharContainer(CharacterContainer):
    """docstring for CharacterContainer"""

    def __init__(self, padded=True):
        super(UncasedCharContainer, self).__init__(
            character_set=(string.digits + string.punctuation +
                           string.ascii_lowercase + ' '),
            padded=padded
        )

    def _process_iter(self, text_iter, **kwargs):
        return map(lambda t: list(t.lower()), text_iter)

    def _process_singleton(self, text, **kwargs):
        return list(text.lower())
