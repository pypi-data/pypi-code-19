#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" 
file: word_container.py
description: a vector storage datastructure for word vectors
author: Luke de Oliveira (lukedeo@vaitech.io)
copyright: 2017 Vai Technologies, LLC. All Rights Reserved.
"""

import logging
import numpy as np

from spacy.en import English

from .token_container import TokenContainer
from .utils import case

logger = logging.getLogger(__name__)

NLP = English()


class WordVectorBoxException(Exception):
    """ Errors for VectorBox. """
    pass


class WordContainer(TokenContainer):
    """docstring for CharacterContainer"""

    def _process_iter(self, text_iter, lower=True, **kwargs):
        pipeline = NLP.pipe(text_iter, **kwargs)
        return ((case(token.text, lower) for token in parsed) for parsed in pipeline)

    def _process_singleton(self, text, lower=True, **kwargs):
        return [case(token.text, lower) for token in NLP(text)]
