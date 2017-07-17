from collections import OrderedDict
from whoosh.filedb.filestore import FileStorage, RamStorage
from whoosh.fields import Schema, ID, KEYWORD, TEXT
from whoosh.qparser import QueryParser


class Index(object):
    """Census API metadata indexer."""

    _SchemaFields = OrderedDict((
        ('api_id', ID(stored=True)),
        ('title', TEXT(stored=True)),
        ('description', TEXT),
        ('variables', KEYWORD(sortable=True)),
        ('geographies', KEYWORD(sortable=True)),
        ('concepts', KEYWORD(sortable=True)),
        ('keywords', KEYWORD(sortable=True)),
        ('tags', KEYWORD(sortable=True)),
        ('vintage', KEYWORD(sortable=True)),
    ))

    _CensusMetadataSchema = Schema(**_SchemaFields)

    def __init__(self, path=None):
        """Initialize Whoosh index for Census API metadata fields"""
        # Initialize index
        fs = FileStorage(path).create() if path else RamStorage()
        if fs.index_exists():
            self.index = fs.open_index()
        else:
            self.index = fs.create_index(self._CensusMetadataSchema)
        if self.index.schema != self._CensusMetadataSchema:
            raise RuntimeError
        # and a query parser
        self.qparser = QueryParser("title", schema=self._CensusMetadataSchema)

    def add(self, iterator):
        """Add entries to the index

        Arguments:
          * iterator: iterator over tuples of field metadata, viz.
            api_id, title, description, variables, geographies, concepts,
            keywords, tags, and vintage.
        """
        with self.index.writer(procs=4) as writer:
            for fieldvals in iterator:
                writer.update_document(
                    **zip(self._SchemaFields.keys(), fieldvals)
                )

    def query(self, querystring):
        """Find API IDs matching querystring"""

        query = self.qparser.parse(querystring)
        with self.index.searcher() as searcher:
            results = searcher.search(query, limit=None)
            return results
