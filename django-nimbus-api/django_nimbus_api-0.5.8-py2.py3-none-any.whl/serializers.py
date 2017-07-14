# -*- coding: utf-8 -*-
from __future__ import absolute_import
from django.utils import six
from rest_framework import serializers
from rest_framework.serializers import SerializerMetaclass


class Serializer(serializers.Serializer):
    pass


class ListSerializer(serializers.ListSerializer):
    pass


class ModelSerializer(serializers.ModelSerializer):
    pass


class HyperlinkedModelSerializer(serializers.HyperlinkedModelSerializer):
    pass
