# -*- coding: utf-8 -*-
"""Sample usage:

    >>> import pyliveleak
    >>> index_page = pyliveleak.login(username, password)
    >>> file_token, item_token = index_page.add_item('tests/test-data/foreman_cif.mp4')
    >>> item_token
    u'b86_1502357642'

Your new video will be available here: https://www.liveleak.com/view?i={item_token}

You may specify optional metadata:

    >>> index_page.add_item('tests/test-data/foreman_cif.mp4', title='my title',
    ...                     body='detailed description', tags='tags', category='World News')

The category must be one of:

    >>> pprint.pprint(sorted(pyliveleak.CATEGORIES))
    ['afghanistan',
     'citizen journalism',
     'conspiracy',
     'creative',
     'history',
     'hobbies',
     'iran',
     'iraq',
     'liveleak challenges',
     'liveleaks',
     'music',
     'nature',
     'other',
     'other entertainment',
     'other items from liveleakers',
     'other middle east',
     'other news',
     'politics',
     'propaganda',
     'regional news',
     'religion',
     'science and technology',
     'sports',
     'syria',
     'ukraine',
     'vehicles',
     'weapons',
     'world news',
     'wtf',
     'yawn',
     'your say']
"""
import os.path as P
from pyliveleak import login, IndexPage, CATEGORIES
__all__ = ('login', 'IndexPage', 'CATEGORIES')

with open(P.join(P.dirname(__file__), 'VERSION')) as fin:
    __version__ = fin.read().strip()
