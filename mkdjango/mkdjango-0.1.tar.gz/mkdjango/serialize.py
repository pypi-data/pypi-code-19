import django.db.models
from django.http import HttpResponse

__author__ = 'Michael'

__SERIALIZE_METHOD_NAME = 'serialize'
__SERIALIZE_EXTEND_METHOD_NAME = 'serialize_extend'


class SerializeProperty(object):
    def __init__(self, func, name):
        self.__func = func
        self.name = name

    def __call__(self, *args, **kwargs):
        return self.__func(*args, **kwargs)


def serialize_property(name=None):
    def __decor(func):
        if name is not None:
            property_name = name
        elif func.__name__.startswith("get_"):
            property_name = func.__name__[4:]
        else:
            property_name = func.__name__

        p = SerializeProperty(func, property_name)

        return p

    return __decor


def serialize(obj):
    if hasattr(obj, __SERIALIZE_METHOD_NAME):
        return getattr(obj, __SERIALIZE_METHOD_NAME)()

    result = {field.name: field.value_from_object(obj)
              for field in obj._meta.get_fields() if isinstance(field, django.db.models.Field)}

    for attr in obj.__class__.__dict__.values():
        if isinstance(attr, SerializeProperty):
            result[attr.name] = attr(obj)

    if not hasattr(obj, __SERIALIZE_EXTEND_METHOD_NAME):
        return result

    result.update(getattr(obj, __SERIALIZE_EXTEND_METHOD_NAME)())
    return result


def is_query_set(obj):
    return isinstance(obj, django.db.models.Manager) or isinstance(obj, django.db.models.QuerySet)


def is_query_object(obj):
    return isinstance(obj, django.db.models.Model)


def is_query_result(obj):
    return is_query_set(obj) or is_query_object(obj)


def serialize_all(obj):
    """
    Recursively iterate through all lists/dicts.
    """
    if is_query_set(obj):
        return [serialize(o) for o in obj.all()]
    elif is_query_object(obj):
        return serialize(obj)

    if isinstance(obj, list):
        for i in range(len(obj)):
            obj[i] = serialize_all(obj[i])
    elif isinstance(obj, dict):
        for key in obj:
            obj[key] = serialize_all(obj[key])

    return obj


class ModelWrapper(object):
    def __init__(self, get_response):
        self.__get_response = get_response

    def __call__(self, request):
        response = self.__get_response(request)

        if isinstance(response, HttpResponse):
            return response

        return serialize_all(response)
