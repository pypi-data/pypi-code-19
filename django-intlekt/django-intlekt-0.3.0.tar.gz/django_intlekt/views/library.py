from rest_framework import mixins
from rest_framework_mongoengine.viewsets import GenericViewSet as MEGenericViewSet
from rest_framework_mongoengine import viewsets as mongoviewsets

from . import utils
from .. import models
from .. import serializers


def viewset_factory(model_name, lookup_field='id'):
    name = model_name + 'ViewSet'
    serializer_class = serializers.__dict__[model_name + 'Serializer']
    model = models.__dict__[model_name]

    def get_queryset(self):
        return model.objects.all()

    def get_view_description(cls, html=False):
        return utils.get_modelview_description(model, html=html)

    return type(
        name,
        (mongoviewsets.ModelViewSet,),
        {
            'queryset': model.objects.all(),
            'lookup_field': lookup_field,
            'serializer_class': serializer_class,
            'get_queryset': get_queryset,
            'get_view_description': classmethod(get_view_description),
        }
    )


GroupViewSet = viewset_factory('Group')
WordViewSet = viewset_factory('Word')
TextViewSet = viewset_factory('Text')


class USLViewSet(mixins.RetrieveModelMixin,
                 mixins.ListModelMixin,
                 MEGenericViewSet):
    queryset = models.USL.objects.all()
    lookup_field = 'id'
    serializer_class = serializers.USLSerializer
    filter_fields = ('ieml_text',)

    @classmethod
    def get_view_description(cls, html=False):
        return utils.get_modelview_description(models.USL, html=html)

    def get_kwargs_for_filtering(self):
        filtering_kwargs = {} 
        for field in  self.filter_fields:
            field_value = self.request.query_params.get(field)
            if field_value: 
                filtering_kwargs[field] = field_value
        return filtering_kwargs 

    def get_queryset(self):
        filtering_kwargs = self.get_kwargs_for_filtering()
        if filtering_kwargs:
            return models.USL.objects(**filtering_kwargs)
        return models.USL.objects.all()
