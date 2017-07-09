import itertools
import os

import nltk
from nltk.corpus import wordnet as wn

class WordNetExpander:

    def __init__(self):

        path = os.path.join(
            os.path.dirname(__file__)
            , 'nltk_data'
        )

        if not path in nltk.data.path:
            nltk.data.path.append(path)

    def _expand(self, kind, word):
        synsets = wn.synsets(word, pos=kind)
        lemma_names = itertools.chain.from_iterable(
            el.lemma_names() for el in synsets
        )

        seen = set()
        def check_seen(el):
            there = el not in seen
            seen.add(el)
            return there

        return itertools.islice(filter(check_seen, lemma_names), 0, 5)

    def verb(self, verb):
        return self._expand(wn.VERB, verb)

    def noun(self, noun):
        return self._expand(wn.NOUN, noun)

    def adj(self, adj):
        return self._expand(wn.ADJ, adj)

    def adv(self, adv):
        return self._expand(wn.ADV, adv)
