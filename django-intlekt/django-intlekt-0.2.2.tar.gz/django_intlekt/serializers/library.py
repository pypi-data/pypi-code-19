from rest_framework_mongoengine import serializers as mongoserializers
from rest_framework import serializers

from . import utils
from .. import models


def validate_translations_dict(translations):
    for lang in translations:
        utils.validate_language(lang)


def validate_text_dependencies_number(dependencies):
    # If there is one dependency only, the objects are considered equal.
    # For instance, a text with one word is the word itself.
    if len(dependencies) < 2:
        raise serializers.ValidationError('Must have two dependencies or more.')


def validate_preference_uniqueness_factory(model):
    def validate(preference):
        if preference is not None and model.objects(preference=preference):
            raise serializers.ValidationError('The preference must be unique.')
    return validate


def validate_preference(p):
    if (
        p is None or p > 0 or
        models.Group.match_lowest_preference_pattern(p) or
        models.Group.match_highest_preference_pattern(p)
    ):
        return

    raise serializers.ValidationError(
        'The preference must be null, strictly positive or equal to {0} or {1}.'.format(
            models.Group.LOWEST_PREFERENCE_VALUE,
            models.Group.HIGHEST_PREFERENCE_VALUE,
        )
    )


def validate_text_dependencies_non_recursivity(dependencies):
    # A text cannot depend on another text. To include a text into another,
    # just copy all its dependencies.
    ids = [dep.id for dep in dependencies]
    usls = models.Text.objects(id__in=ids)
    if usls:
        raise serializers.ValidationError(
            'A text cannot contain another text. '
            'Instead, copy all its dependencies.'
        )


def usl_serializer_factory(model_name, extra_kwargs=None):
    name = model_name + 'Serializer'
    Model = models.__dict__[model_name]
    extra_kwargs_ = extra_kwargs or {}

    class Meta:
        model = Model
        exclude = ('_cls',)
        extra_kwargs = {
            'translations': {'validators': [validate_translations_dict]},
            **extra_kwargs_,
        }

    return type(name, (mongoserializers.DocumentSerializer,), {'Meta': Meta})


class USLSerializer(mongoserializers.DocumentSerializer):
    class Meta:
        model = models.USL
        fields = '__all__'


TextSerializer = usl_serializer_factory(
    'Text',
    extra_kwargs={
        'dependencies': {
            'validators': [
                utils.validate_set,
                validate_text_dependencies_number,
                validate_text_dependencies_non_recursivity,
            ]
        }
    }
)


WordSerializer = usl_serializer_factory('Word')


def group_serializer_factory(model_name, children_field, extra_kwargs=None):
    name = model_name + 'Serializer'
    Model = models.__dict__[model_name]
    extra_kwargs_ = extra_kwargs or {}
    extra_kwargs_[children_field] = {'validators': [utils.validate_set]}

    class Meta:
        model = Model
        fields = '__all__'
        extra_kwargs = {
            'preference': {
                'validators': [
                    validate_preference_uniqueness_factory(Model),
                    validate_preference,
                ],
                'min_value': min(
                    Model.LOWEST_PREFERENCE_VALUE,
                    Model.HIGHEST_PREFERENCE_VALUE
                ),
            },
            **extra_kwargs_,
        }

    def parse_preference(self, validated_data):
        key = 'preference'
        pos = validated_data.get(key)

        if Model.match_lowest_preference_pattern(pos):
            validated_data[key] = Model.get_lowest_preference()
        elif Model.match_highest_preference_pattern(pos):
            validated_data[key] = Model.get_highest_preference()

    serializer_class = type(name, (mongoserializers.DocumentSerializer,), {
        'Meta': Meta,
        'parse_preference': parse_preference,
    })

    # These methods are defined outside the call above because we need the
    # class to call `super`.
    def create(self, validated_data):
        self.parse_preference(validated_data)
        return super(serializer_class, self).create(validated_data)
    setattr(serializer_class, 'create', create)

    def update(self, instance, validated_data):
        self.parse_preference(validated_data)
        return super(serializer_class, self).update(instance, validated_data)
    setattr(serializer_class, 'update', update)

    return serializer_class


GlossarySerializer = group_serializer_factory('Glossary', 'terms')
LexiconSerializer = group_serializer_factory('Lexicon', 'words')
