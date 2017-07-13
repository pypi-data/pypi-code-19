from django.apps import apps
from django import template

from ..menu import RootMenu


register = template.Library()

@register.simple_tag(takes_context=True)
def menu(context):
    menu = RootMenu(context['request'])
    for config in apps.get_app_configs():
        if not hasattr(config, 'menu'):
            continue
        if isinstance(config.menu, (list, tuple)):
            for item in config.menu:
                menu.add(item)
        else:
            menu.add(config.menu)
    return str(menu)
