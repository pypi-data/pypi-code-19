# coding: utf-8
"""
This module provides redefined DRF's generic views and viewsets leveraging serializer registration.

One of the main issues with creating traditional DRF APIs is a lot of bloat (and we're writing Python, not Java or C#,
to avoid bloat) that's completely unnecessary in a structured Django project. Therefore this module aims to provide
a better and simpler way to write simple API endpoints - without limiting the ability to create more complex views.
The particular means to that end are:
* :class:`rest_easy.scopes.ScopeQuerySet` and its subclasses (
  :class:`rest_easy.scopes.UrlKwargScopeQuerySet` and
  :class:`rest_easy.scopes.RequestAttrScopeQuerySet`) provide a simple way to scope views and viewsets
  by resource (ie. limiting results to single account, or /resource/<resource_pk>/inner_resource/<inner_resource_pk>/)
* generic views leveraging the above, as well as model-and-schema specification instead of queryset, serializer and
  helper methods - all generic views that were available in DRF as well as GenericAPIView are redefined to support
  this.
* Generic :class:`rest_easy.views.ModelViewSet` which allows for very simple definition of resource
  endpoint.

To make the new views work, all that's required is a serializer:

```python
from users.models import User
from accounts.models import Account
from rest_easy.serializers import ModelSerializer
class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'
        schema = 'default'

class UserViewSet(ModelViewSet):
    model = User
    scope = UrlKwargScopeQuerySet(Account)
```

and in urls.py:

```python
from django.conf.urls import url, include
from rest_framework.routers import DefaultRouter
router = DefaultRouter()
router.register(r'accounts/(?P<account_pk>[0-9]+)/users', UserViewSet)
urlpatterns = [url(r'^', include(router.urls))]
```

The above will provide the users scoped by account primary key as resources: with list, retrieve, create, update and
partial update methods, as well as standard HEAD and OPTIONS autogenerated responses.

You can easily add custom paths to viewsets when needed - it's described in DRF documentation.
"""
from __future__ import unicode_literals

from django.conf import settings
from rest_framework.viewsets import ViewSetMixin
from rest_framework import generics, mixins
from six import with_metaclass

from rest_easy.exceptions import RestEasyException
from rest_easy.registers import serializer_register
from rest_easy.scopes import ScopeQuerySet


class ScopedViewMixin(object):
    """
    This class provides a get_queryset method that works with ScopeQuerySet.

    Queryset obtained from superclass is filtered by view.scope's (if it exists) child_queryset() method.
    """

    def get_queryset(self):
        """
        Calls scope's child_queryset methods on queryset as obtained from superclass.
        :return: queryset.
        """
        queryset = super(ScopedViewMixin, self).get_queryset()
        if hasattr(self, 'scope'):
            if isinstance(self.scope, ScopeQuerySet):
                queryset = self.scope.child_queryset(queryset, self)
            else:
                for scope in self.scope:
                    queryset = scope.child_queryset(queryset, self)
        return queryset


class ViewEasyMetaclass(type):
    """
    This metaclass sets default queryset on a model-and-schema based views and fills in concrete views with bases.

    It's required for compatibility with some of DRF's elements, like routers.
    """
    resolved_bases = None

    @classmethod
    def get_additional_bases(mcs):
        """
        Looks for additional view bases in settings.REST_EASY_VIEW_BASES
        :return:
        """
        if mcs.resolved_bases is None:
            mcs.resolved_bases = []
            from importlib import import_module
            for base in getattr(settings, 'REST_EASY_VIEW_BASES'):
                mod, cls = base.rsplit('.', 1)
                mcs.resolved_bases.append(getattr(import_module(mod), cls))

        return mcs.resolved_bases

    def __new__(mcs, name, bases, attrs):
        """
        Create the class.
        """
        if ('queryset' not in attrs or attrs['queryset'] is None) and 'model' in attrs:
            attrs['queryset'] = attrs['model'].objects.all()
        if (not attrs.get('__abstract__', False)) and 'parent' in attrs and isinstance(attrs['parent'], ScopeQuerySet):
            attrs['parent'] = [attrs['parent']]
        bases = tuple(mcs.get_additional_bases() + list(bases))
        return super(ViewEasyMetaclass, mcs).__new__(mcs, name, bases, attrs)


class ChainingCreateUpdateMixin(object):
    """
    Chain-enabled versions of perform_create and perform_update.
    """
    def perform_create(self, serializer, **kwargs):  # pylint: disable=no-self-use
        """
        Extend default implementation with kwarg chaining.
        """
        return serializer.save(**kwargs)

    def perform_update(self, serializer, **kwargs):  # pylint: disable=no-self-use
        """
        Extend default implementation with kwarg chaining.
        """
        return serializer.save(**kwargs)


class GenericAPIViewBase(ScopedViewMixin, generics.GenericAPIView):
    """
    Provides a base for all generic views and viewsets leveraging registered serializers and ScopeQuerySets.

    Adds additional DRF-verb-wise override for obtaining serializer class: serializer_schema_for_verb property.
    It should be a dictionary of DRF verbs and serializer schemas (they work in conjunction with model property).
    The priority for obtaining serializer class is:
    * get_serializer_class override
    * serializer_class property
    * model + serializer_schema_for_verb[verb] lookup in :class:`rest_easy.registers.SerializerRegister`
    * model + schema lookup in :class:`rest_easy.registers.SerializerRegister`
    """
    serializer_schema_for_verb = {}

    def get_drf_verb(self):
        """
        Obtain the DRF verb used for a request.
        """
        method = self.request.method.lower()
        if method == 'get':
            if self.lookup_url_kwarg in self.kwargs:
                return 'retrieve'
            return 'list'
        mapping = {
            'post': 'create',
            'put': 'update',
            'patch': 'partial_update',
            'delete': 'destroy'
        }
        return mapping[method]

    def get_serializer_name(self, verb=None):
        """
        Obtains registered serializer name for this view.

        Leverages :class:`rest_easy.registers.SerializerRegister`. Works when either of or both model
        and schema properties are available on this view.

        :return: registered serializer key.
        """
        model = getattr(self, 'model', None)
        schema = None
        if not model and not hasattr(self, 'schema') and (verb and verb not in self.serializer_schema_for_verb):
            raise RestEasyException('Either model or schema fields need to be set on a model-based GenericAPIView.')
        if verb:
            schema = self.serializer_schema_for_verb.get(verb, None)
        if schema is None:
            schema = getattr(self, 'schema', 'default')
        return serializer_register.get_name(model, schema)

    def get_serializer_class(self):
        """
        Gets serializer appropriate for this view.

        Leverages :class:`rest_easy.registers.SerializerRegister`. Works when either of or both model
        and schema properties are available on this view.

        :return: serializer class.
        """

        if hasattr(self, 'serializer_class') and self.serializer_class:
            return self.serializer_class

        serializer = serializer_register.lookup(self.get_serializer_name(verb=self.get_drf_verb()))
        if serializer:
            return serializer

        raise RestEasyException('Serializer for model {} and schema {} cannot be found.'.format(
            getattr(self, 'model', '[no model]'),
            getattr(self, 'schema', '[no schema]')
        ))


class GenericAPIView(with_metaclass(ViewEasyMetaclass, GenericAPIViewBase)):
    """
    Base view with compat metaclass.
    """
    __abstract__ = True


class CreateAPIView(ChainingCreateUpdateMixin,
                    mixins.CreateModelMixin,
                    GenericAPIView):
    """
    Concrete view for creating a model instance.
    """

    def post(self, request, *args, **kwargs):
        """
        Shortcut method.
        """
        return self.create(request, *args, **kwargs)


class ListAPIView(mixins.ListModelMixin,
                  GenericAPIView):
    """
    Concrete view for listing a queryset.
    """

    def get(self, request, *args, **kwargs):
        """
        Shortcut method.
        """
        return self.list(request, *args, **kwargs)


class RetrieveAPIView(mixins.RetrieveModelMixin,
                      GenericAPIView):
    """
    Concrete view for retrieving a model instance.
    """

    def get(self, request, *args, **kwargs):
        """
        Shortcut method.
        """
        return self.retrieve(request, *args, **kwargs)


class DestroyAPIView(mixins.DestroyModelMixin,
                     GenericAPIView):
    """
    Concrete view for deleting a model instance.
    """

    def delete(self, request, *args, **kwargs):
        """
        Shortcut method.
        """
        return self.destroy(request, *args, **kwargs)


class UpdateAPIView(ChainingCreateUpdateMixin,
                    mixins.UpdateModelMixin,
                    GenericAPIView):
    """
    Concrete view for updating a model instance.
    """

    def put(self, request, *args, **kwargs):
        """
        Shortcut method.
        """
        return self.update(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        """
        Shortcut method.
        """
        return self.partial_update(request, *args, **kwargs)


class ListCreateAPIView(ChainingCreateUpdateMixin,
                        mixins.ListModelMixin,
                        mixins.CreateModelMixin,
                        GenericAPIView):
    """
    Concrete view for listing a queryset or creating a model instance.
    """

    def get(self, request, *args, **kwargs):
        """
        Shortcut method.
        """
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        """
        Shortcut method.
        """
        return self.create(request, *args, **kwargs)


class RetrieveUpdateAPIView(ChainingCreateUpdateMixin,
                            mixins.RetrieveModelMixin,
                            mixins.UpdateModelMixin,
                            GenericAPIView):
    """
    Concrete view for retrieving, updating a model instance.
    """

    def get(self, request, *args, **kwargs):
        """
        Shortcut method.
        """
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        """
        Shortcut method.
        """
        return self.update(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        """
        Shortcut method.
        """
        return self.partial_update(request, *args, **kwargs)


class RetrieveDestroyAPIView(mixins.RetrieveModelMixin,
                             mixins.DestroyModelMixin,
                             GenericAPIView):
    """
    Concrete view for retrieving or deleting a model instance.
    """

    def get(self, request, *args, **kwargs):
        """
        Shortcut method.
        """
        return self.retrieve(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        """
        Shortcut method.
        """
        return self.destroy(request, *args, **kwargs)


class RetrieveUpdateDestroyAPIView(ChainingCreateUpdateMixin,
                                   mixins.RetrieveModelMixin,
                                   mixins.UpdateModelMixin,
                                   mixins.DestroyModelMixin,
                                   GenericAPIView):
    """
    Concrete view for retrieving, updating or deleting a model instance.
    """

    def get(self, request, *args, **kwargs):
        """
        Shortcut method.
        """
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        """
        Shortcut method.
        """
        return self.update(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        """
        Shortcut method.
        """
        return self.partial_update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        """
        Shortcut method.
        """
        return self.destroy(request, *args, **kwargs)


class GenericViewSet(ViewSetMixin, GenericAPIView):
    """
    The GenericViewSet class does not provide any actions by default,
    but does include the base set of generic view behavior, such as
    the `get_object` and `get_queryset` methods.
    """
    pass


class ReadOnlyModelViewSet(mixins.RetrieveModelMixin,
                           mixins.ListModelMixin,
                           GenericViewSet):
    """
    A viewset that provides default `list()` and `retrieve()` actions.
    """
    pass


class ModelViewSet(ChainingCreateUpdateMixin,
                   mixins.CreateModelMixin,
                   mixins.RetrieveModelMixin,
                   mixins.UpdateModelMixin,
                   mixins.DestroyModelMixin,
                   mixins.ListModelMixin,
                   GenericViewSet):
    """
    A viewset that provides default `create()`, `retrieve()`, `update()`,
    `partial_update()`, `destroy()` and `list()` actions.
    """
    pass
