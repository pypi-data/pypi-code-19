import os

from django import template
from django.apps import apps
from django.templatetags.static import StaticNode

register = template.Library()


@register.simple_tag(name='webpack_static')
def webpack_static(path):
    """
    Translates a given path to
    :param path: Path to a static file
    :return: Chained call to static
    """

    node = apps.app_configs['webpack_static'].mapping

    try:
        tokens = os.path.split(path)
        for token in tokens:
            node = node[token]

        result_tokens = list(tokens[:-1]) + [node]
        result_path = os.path.join(*result_tokens)
    except KeyError:
        result_path = path

    return StaticNode.handle_simple(result_path)
