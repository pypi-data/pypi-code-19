import pycountry
from slugify import slugify

from rest_framework import serializers


def validate_set(list_):
    if len(set(list_)) != len(list_):
        raise serializers.ValidationError('Cannot have duplicates.')


def validate_language(language):
    try:
        pycountry.languages.get(alpha_2=language)
    except KeyError:
        raise serializers.ValidationError('Bad format. See ISO 639-1.')


def validate_slug(text):
    slug = slugify(text)
    if text != slug:
        raise serializers.ValidationError(
            'Invalid slug, should be "{0}".'.format(slug)
        )
