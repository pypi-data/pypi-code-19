from rest_framework_mongoengine import serializers as mongoserializers
from rest_framework_mongoengine.validators import UniqueValidator
from rest_framework import serializers

from . import utils
from .. import models


def validate_sources_dict(sources):
    for key, source in sources.items():
        if key != source['id']:
            raise serializers.ValidationError(
                "The key '{0}' must be equal to the 'id' field value "
                "'{1}'.".format(key, source['id'])
            )


def validate_posts_dict(posts):
    for key, post in posts.items():
        if key != str(post['document'].id):
            raise serializers.ValidationError(
                "The key '{0}' must be equal to the 'document' field value "
                "'{1}'.".format(key, post['document'].id)
            )


class CollectedSourceSerializer(mongoserializers.EmbeddedDocumentSerializer):
    class Meta:
        model = models.CollectedSource
        fields = '__all__'
        read_only_fields = ('id',) 
        extra_kwargs = {
            'last_request_date': {
                'format': '%Y-%m-%d',
                'input_formats': ['%Y-%m-%d'],
            },
        }


class PostSerializer(mongoserializers.EmbeddedDocumentSerializer):
    class Meta:
        model = models.Post
        fields = '__all__'
        extra_kwargs = {
            'collected_on': {
                'format': '%Y-%m-%d',
                'input_formats': ['%Y-%m-%d'],
            },
            'description': {'allow_blank': True},
            'tags': {'validators': [utils.validate_set]},
        }


class CollectionSerializer(mongoserializers.DocumentSerializer):
    class Meta:
        model = models.Collection
        fields = '__all__'
        read_only_fields = ('created_on', 'updated_on',)
        extra_kwargs = {
            'created_on': {'format': '%Y-%m-%d'},
            'updated_on': {'format': '%Y-%m-%d'},
            'authors': {'validators': [utils.validate_set]},
            'posts': {
                'child': PostSerializer(),
                'validators': [validate_posts_dict],
            },
            'sources': {
                'child': CollectedSourceSerializer(),
                'validators': [validate_sources_dict],
            },
        }


class DocumentSerializer(mongoserializers.DocumentSerializer):
    class Meta:
        model = models.Document
        fields = '__all__'
        extra_kwargs = {
            'created_on': {
                'format': '%Y-%m-%d',
                'input_formats': ['%Y-%m-%d'],
            },
            'authors': {'validators': [utils.validate_set]},
            'keywords': {'validators': [utils.validate_set]},
            'language': {'validators': [utils.validate_language]},
            'title': {'allow_blank': True},
        }


class TagSerializer(mongoserializers.DocumentSerializer):
    slug = serializers.CharField(
        required=True,
        validators=[
            UniqueValidator(queryset=models.Tag.objects),
            utils.validate_slug,
        ],
    )

    class Meta:
        model = models.Tag
        fields = '__all__'
        extra_kwargs = {
            'usls': {'validators': [utils.validate_set]},
        }


class SourceSerializer(mongoserializers.DocumentSerializer):
    class Meta:
        model = models.Source
        fields = '__all__'


class SourceDriverSerializer(mongoserializers.DocumentSerializer):
    class Meta:
        model = models.SourceDriver
        fields = '__all__'
