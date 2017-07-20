"""
Author: Amol Kapoor
Description: Handles text indexing of files with Whoosh.
"""

import codecs
import os

from whoosh.index import create_in
from whoosh.fields import *
from whoosh.qparser import QueryParser

import os

INDEX_DIR = os.path.join(os.path.dirname(__file__), 'indexdir')

def index_text(files):
    """Goes through all files passed in and indexes text"""
    schema = Schema(path=ID(stored=True), last_mod=NUMERIC(stored=True),
                    content=TEXT)
    ix = create_in(INDEX_DIR, schema)
    writer = ix.writer()

    for f in files:
        try:
            with codecs.open(f, 'r', 'utf-8') as openf:
                writer.add_document(path=unicode(f, 'utf-8'),
                                    content=openf.read(),
                                    last_mod=os.path.getmtime(f))
        except:
            continue

    writer.commit()
    return ix

def search_text(ix, user_query):
    """Searches all indexed files and returns paths of hits."""
    with ix.searcher() as searcher:
        query = QueryParser("content", ix.schema).parse(user_query)
        results = searcher.search(query, limit=None)
        results.fragmenter.charlimit = None
        returned_results = {}
        for result in results:
            path = result['path'].encode('ascii', 'ignore')
            last_mod = result['last_mod']
            with codecs.open(path, 'r', 'utf-8') as f:
                content = f.read()
                highlight = result.highlights('content', text=content)
                returned_results[path] = {'highlight': highlight,
                                          'last_mod': last_mod}

        return returned_results
