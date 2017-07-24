import os
import elasticsearch
import inspect
import six

from collections import namedtuple
from contextlib import contextmanager
from six.moves import filter

from elasticsearch_dsl.document import DocType, DocTypeMeta
from elasticsearch_dsl.connections import connections

from .analysis_utils import AnalysisDefinition
from .fields import FlexField
from .utils import rgetattr
from .query import DocAccessors
from .search_templates import SearchTemplate

_MODEL_INDEX_MAPPING = {}

FieldAttrMap = namedtuple('FieldAttrMap', ('name', 'attr'))


class IndexableMeta(type):
    '''Defines an introspection type for Indexable Models.'''
    def __new__(cls, name, bases, namespace):
        fields = []
        # We introspect and collect the names of all the Fields in Index
        # to facilitate differentiating field attribute from non-field attribute
        # later.
        for k, x in namespace.items():
            if isinstance(x, FlexField):
                f = x._model_attr if x._model_attr is not None else k
                fields.append(FieldAttrMap(k, f))
        # Append field-name information from all the Base classes.
        ix_predicate = lambda x: issubclass(x, DocType) and hasattr(x, '_fields')
        for base_index in filter(ix_predicate, bases):
            fields.extend(base_index._fields)
        # Insert fields into this class's namespace.
        namespace['_fields'] = fields

        # Make a reference of Meta in the object namespace (would not be GCd)
        if 'Meta' in namespace:
            namespace['_meta'] = namespace['Meta']

        # TODO: Assert sanity of extension class
        # -- Implement checking get_queryset and get_model implementations.
        klass = super(IndexableMeta, cls).__new__(cls, name, bases, namespace)
        # Register this doctype in indexed models mapping.
        if 'model' in namespace:
            _MODEL_INDEX_MAPPING[namespace['model']] = klass
        klass.docs = DocAccessors(klass)
        return klass


class IndexableDocTypeMeta(IndexableMeta, DocTypeMeta):
    pass


@six.python_2_unicode_compatible
@six.add_metaclass(IndexableDocTypeMeta)
class IndexedModel(DocType):
    '''Base class for declaring Index for a Model.

    This class is an extension of Elasticsearch-DSL's DocType. For the fields,
    as a convention, it is assumed that the model has the attribute of the
    same name. This default behaviour can be controlled by implementing a
    `prepare_<FieldName>` method, accepting the object instance.
    '''
    def get_queryset(self):
        return self.queryset

    def get_object(self):
        qs = self.get_queryset()
        return qs.get(pk=self._id)

    @property
    def object(self):
        return self.get_object()

    @property
    def index_name(self):
        return self._doc_type.index

    def prepare(self):
        obj = self.get_object()
        for field in self._fields:
            try:
                prep_method = getattr(self, 'prepare_{0}'.format(field.attr))
                setattr(self, field.name, prep_method(obj))
            except AttributeError:
                val_from_obj_attr = rgetattr(obj, field.attr)
                setattr(self, field.name, val_from_obj_attr)

    @classmethod
    def init_using_pk(cls, pk):
        obj = cls(_id=pk)
        return obj

    @classmethod
    def init(cls, index=None, using=None):
        ix_name = cls._doc_type.index
        module_dir = os.path.dirname(inspect.getabsfile(cls))
        tpl_dir = os.path.join(module_dir, 'search_templates')

        # Init mapping
        cls._doc_type.init(index, using)

        # Discover and register the Templates and Analyzers.
        if hasattr(cls, '_meta'):
            # Use the instance for registering analyzers.
            self = cls()
            for tpl in getattr(cls._meta, 'query_templates', []):
                identifier = '.'.join([ix_name, tpl])
                template_file = os.path.join(tpl_dir, '{}.json'.format(tpl))
                template = SearchTemplate(identifier, template_file)
                template.register(self)

            for analyzer in getattr(cls._meta, 'analyzers', []):
                definition = AnalysisDefinition(analyzer)
                definition.register(self)

    @staticmethod
    def get_connection():
        return connections.get_connection()

    def delete_index(self):
        return self.get_connection().indices.delete(self.index_name)

    def close(self):
        try:
            self.get_connection().indices.close(self.index_name)
        except elasticsearch.exceptions.NotFoundError:
            # We ignore the NotFoundError when a non-existent index is attempted
            # to be closed. This is for convinience in context manager.
            pass

    def open(self):
        self.get_connection().indices.open(self.index_name)

    @contextmanager
    def ensure_closed_and_reopened(self):
        self.close()
        yield self
        self.open()

    def __repr__(self):
        return '<{0} index={1}>'.format(self.__class__.__name__, self._index)

    def __str__(self):
        return repr(self)


def get_index_for_model(model):
    try:
        return _MODEL_INDEX_MAPPING[model]
    except KeyError:
        raise KeyError('Model {0} has no associated index'.format(model))


def get_model_for_index(index):
    try:
        rev_map = (m for m, i in _MODEL_INDEX_MAPPING.items() if i is index)
        return next(rev_map, None)
    except StopIteration:
        raise KeyError('Index {0} has no associated model'.format(index))


def registered_indices():
    return _MODEL_INDEX_MAPPING.values()


__all__ = (
    'IndexedModel',
    'get_index_for_model',
    'get_model_for_index',
    'registered_indices',
)
