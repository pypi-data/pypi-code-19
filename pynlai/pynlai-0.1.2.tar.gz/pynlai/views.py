# -*- coding: utf-8 -*-

'''
views
-----

defines field views for spacy objects.
'''


_DEP_SPAN = {
    'MR': (
        'vector_norm',
        'root.orth',
        'root.lemma',
        'root.dep',
        'root.head.orth',
        'root.head.lemma',
        'root.head.pos',
    ),
    'HR': (
        'text',
        'root.orth_',
        'root.lemma_',
        'root.dep_',
        'root.head.orth_',
        'root.head.lemma_',
        'root.head.pos_',
    ),
}

_DEP_TOKEN = {
    'MR': (
        'orth',
        'lemma',
        'dep',
        'head.orth',
        'head.lemma',
        'head.pos',
    ),
    'HR': (
        'orth_',
        'lemma_',
        'dep_',
        'head.orth_',
        'head.lemma_',
        'head.pos_',
    ),
}

_ENT_SPAN = {
    'MR': (
        'vector_norm',
        'label',
    ),
    'HR': (
        'text',
        'label_',
    ),
}

_POS_TOKEN = {
    'MR': (
        'orth',
        'pos',
        'lemma',
    ),
    'HR': (
        'orth_',
        'pos_',
        'lemma_',
    ),
}
