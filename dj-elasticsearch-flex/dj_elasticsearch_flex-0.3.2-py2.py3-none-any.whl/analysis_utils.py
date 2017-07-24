import logging

from elasticsearch_dsl.analysis import CustomAnalyzer

logger = logging.getLogger(__name__)


class AnalysisDefinition(object):
    '''
    This defines a helper class for registering search analyzers.
    Analyzers can be defined as callables, hence ensuring io/cpu bound analysis
    configuration can be deffered until necessary.

    An example use case of this is in defining Synonym Token Filter, where
    the Synonyms may be loaded from a network file. This is only necessary when
    the index is actually being set up, hence a callable would ensure that
    the synonyms fie is not downloaded at all the time.
    '''

    def __init__(self, params):
        self.definition = self._get_definition(params)

    def _get_definition(self, anz):
        if callable(anz):
            # A callable definition may return either a CustomAnalyzer or a dict.
            # We recursively process the return value.
            return self._get_definition(anz())
        elif isinstance(anz, CustomAnalyzer):
            # For CustomAnalyzer, we use the definition.
            return anz.get_analysis_definition()
        elif isinstance(anz, dict):
            # Use dicts as it is.
            return anz
        raise ValueError('Analyzer can be a callable, DSL CustomAnalyzer, or a dict.')

    def register(self, index):
        body = {'analysis': self.definition}
        with index.ensure_closed_and_reopened() as ix:
            conn = ix.get_connection()
            conn.indices.put_settings(body=body, index=ix.index_name)
