from django.utils.encoding import smart_text
from rest_framework_mongoengine import viewsets as mongoviewsets
from rest_framework import viewsets
from rest_framework import status
from rest_framework.response import Response
from rest_framework.utils import formatting
from rest_framework.decorators import detail_route

from . import utils
from .. import models
from .. import serializers


class NestedObjectDoesNotExist(LookupError): pass


class NestedCollectionResourceViewSet(viewsets.ViewSet):
    serializer_class = None
    model = None
    resource_name = None

    @staticmethod
    def nested_obj_to_key(obj):
        raise NotImplementedError()

    def get_serializer(self, *args, **kwargs):
        return self.serializer_class(*args, **kwargs)

    @classmethod
    def get_view_description(cls, html=False):
        return utils.get_modelview_description(cls.model, html=html)

    @classmethod
    def get_nested_object(cls, collection_id, object_id):
        try:
            collection = models.Collection.objects.get(id=collection_id)
        except models.Collection.DoesNotExist:
            raise NestedObjectDoesNotExist()

        objects = getattr(collection, cls.resource_name)
        try:
            return objects[object_id], collection
        except KeyError:
            raise NestedObjectDoesNotExist()

    def list(self, request, collection_id=None):
        if collection_id is None:
            return Response('Please specify a collection id.',
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            collection = models.Collection.objects.get(id=collection_id)
        except models.Collection.DoesNotExist:
            return Response('No such collection {}'.format(collection_id),
                            status=status.HTTP_404_NOT_FOUND)
        objects = getattr(collection, self.resource_name)

        for key in objects:
            objects[key] = self.serializer_class(objects[key]).data

        return Response(objects)

    def create(self, request, collection_id=None):
        if collection_id is None:
            return Response('Please specify a collection id.',
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            collection = models.Collection.objects.get(id=collection_id)
        except models.Collection.DoesNotExist:
            return Response('No such collection {}'.format(collection_id),
                            status=status.HTTP_404_NOT_FOUND)

        serializer = self.serializer_class(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)

        obj = serializer.save()

        if self.nested_obj_to_key(obj) in getattr(collection, self.resource_name):
            return Response(
                {self.resource_name: ('This document has already been collected. '
                              'Please, use PUT or PATCH.')},
                status=status.HTTP_400_BAD_REQUEST
            )

        getattr(collection, self.resource_name)[self.nested_obj_to_key(obj)] = obj
        collection.save()

        return Response(serializer.data)

    def retrieve(self, request, pk=None, collection_id=None):
        try:
            obj, _ = self.get_nested_object(collection_id, pk)
        except NestedObjectDoesNotExist:
            return Response(
                'No such object {} in collection {} {}'.format(
                    pk,
                    collection_id,
                    self.resource_name,
                ),
                status=status.HTTP_404_NOT_FOUND
            )

        return Response(self.serializer_class(obj).data)

    def update(self, request, pk=None, collection_id=None):
        try:
            obj, collection = self.get_nested_object(collection_id, pk)
        except NestedObjectDoesNotExist:
            return Response(
                'No such object {} in collection {} {}'.format(
                    pk,
                    collection_id,
                    self.resource_name,
                ),
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = self.serializer_class(obj, data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)

        obj = serializer.save()
        getattr(collection, self.resource_name)[pk] = obj
        collection.save()

        return Response(serializer.data)

    def partial_update(self, request, pk=None, collection_id=None):
        try:
            obj, collection = self.get_nested_object(collection_id, pk)
        except NestedObjectDoesNotExist:
            return Response(
                'No such object {} in collection {} {}'.format(
                    pk,
                    collection_id,
                    self.resource_name,
                ),
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = self.serializer_class(
            obj,
            data=request.data,
            partial=True,
        )
        if not serializer.is_valid():
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)

        obj = serializer.save()
        getattr(collection, self.resource_name)[pk] = obj
        collection.save()

        return Response(serializer.data)

    def destroy(self, request, pk=None, collection_id=None):
        try:
            _, collection = self.get_nested_object(collection_id, pk)
        except NestedObjectDoesNotExist:
            return Response(
                'No such object {} in collection {} {}'.format(
                    pk,
                    collection_id,
                    self.resource_name
                ),
                status=status.HTTP_404_NOT_FOUND
            )

        getattr(collection, self.resource_name).pop(pk, None)
        collection.save()

        return Response('')


class PostViewSet(NestedCollectionResourceViewSet):
    serializer_class = serializers.PostSerializer
    model = models.Post
    resource_name = 'posts'

    @staticmethod
    def nested_obj_to_key(post):
        return str(post.document.id)


class CollectedSourceViewSet(NestedCollectionResourceViewSet):
    serializer_class = serializers.CollectedSourceSerializer
    model = models.CollectedSource
    resource_name = 'sources'

    @staticmethod
    def nested_obj_to_key(source):
        # If the source is created source.id == None, which is not a valid
        # dict key
        return source.id or ''


class CollectionViewSet(mongoviewsets.ModelViewSet):
    queryset = models.Collection.objects.all()
    lookup_field = 'id'
    serializer_class = serializers.CollectionSerializer

    @classmethod
    def get_view_description(cls, html=False):
        return utils.get_modelview_description(models.Collection, html=html)

    def get_queryset(self):
        return models.Collection.objects.all()


class DocumentViewSet(mongoviewsets.ModelViewSet):
    queryset = models.Document.objects.all()
    lookup_field = 'id'
    serializer_class = serializers.DocumentSerializer

    @classmethod
    def get_view_description(cls, html=False):
        return utils.get_modelview_description(models.Document, html=html)

    def get_queryset(self):
        return models.Document.objects.all()


class TagViewSet(mongoviewsets.ModelViewSet):
    queryset = models.Tag.objects.all()
    lookup_field = 'slug'
    serializer_class = serializers.TagSerializer

    @classmethod
    def get_view_description(cls, html=False):
        return utils.get_modelview_description(models.Tag, html=html)

    def get_queryset(self):
        return models.Tag.objects.all()


class SourceViewSet(mongoviewsets.ModelViewSet):
    queryset = models.Source.objects.all()
    lookup_field = 'id'
    serializer_class = serializers.SourceSerializer

    @classmethod
    def get_view_description(cls, html=False):
        return utils.get_modelview_description(models.Source, html=html)

    def get_queryset(self):
        return models.Source.objects.all()


class SourceDriverViewSet(mongoviewsets.ModelViewSet):
    queryset = models.SourceDriver.objects.all()
    lookup_field = 'id'
    serializer_class = serializers.SourceDriverSerializer

    @classmethod
    def get_view_description(cls, html=False):
        return utils.get_modelview_description(models.SourceDriver, html=html)

    def get_queryset(self):
        return models.SourceDriver.objects.all()
