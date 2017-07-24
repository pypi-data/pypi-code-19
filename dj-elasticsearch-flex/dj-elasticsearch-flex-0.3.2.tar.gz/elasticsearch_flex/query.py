'''Search Queryset

This search queryset wraps the low level elasticsearch queries, and acts as
a transparent interface between elasticsearch documents and corresponding
django model objects.
'''
from collections import namedtuple
from elasticsearch_dsl.search import Search

from . import connections


def from_queryset(hits, qs):
    ids = [hit._id for hit in hits]
    objects = qs.in_bulk(ids)
    keytype = type(objects.keys()[0])
    pks = list(map(keytype, ids))
    return pks, [objects[i] for i in pks if i in objects]


class ModelSearch(Search):
    def objects(self, qs=None):
        docs = list(self)
        if len(docs):
            if qs is None:
                # Use one document for introspection.
                # This resolves the default queryset defined with index.
                qs = docs[0].get_queryset()
            _, objects = from_queryset(docs, qs)
            return objects
        return []


class TemplateSearch(ModelSearch):
    def execute(self, ignore_cache=False):
        if ignore_cache or not hasattr(self, '_response'):
            es = connections.get_connection(self._using)
            payload = {
                'id': self._extra['t_name'],
                'params': self._params,
            }

            self._response = self._response_class(
                self,
                es.search_template(
                    index=self._index,
                    doc_type=self._doc_type,
                    body=payload,
                )
            )
        return self._response


class DocAccessors(object):
    def __init__(self, index):
        self.index = index

    @property
    def dsl(self):
        return ModelSearch().doc_type(self.index)

    @property
    def templates(self):
        index_name = self.index._meta.index
        available_templates = getattr(self.index._meta, 'query_templates', [])

        FlexTemplates = namedtuple('FlexTemplates', available_templates)
        dsl = []
        for _id in available_templates:
            tid = index_name + '.' + _id
            s = TemplateSearch(index=index_name, extra={'t_name': tid}, doc_type=self.index)
            dsl.append(s)

        return FlexTemplates(*dsl)
