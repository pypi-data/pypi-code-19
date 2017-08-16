import base64

import coreapi
from django.template import loader
from django.utils.safestring import mark_safe
from rest_framework.compat import template_render
from rest_framework.renderers import BaseRenderer


class ApiJsRenderer(BaseRenderer):
    media_type = 'application/javascript'
    format = 'javascript'
    charset = 'utf-8'
    template = 'drf_api_actions/api.js.tmpl'

    @classmethod
    def render_link(cls, keys, link):
        s = '({arguments}) => action(schema, {keys}'.format(
            arguments=cls.render_arguments(link),
            keys=keys,
        )
        params = cls.render_params(link)
        if params:
            s += ', {{{}}}),'.format(params)
        else:
            s += '),'
        return s

    @classmethod
    def render_arguments(cls, link):
        li = []
        for field in link.fields:
            if field.required:
                s = field.name
            else:
                s = '{}=undefined'.format(field.name)
            li.append(s)
        return ', '.join(li)

    @classmethod
    def render_params(cls, link):
        return ', '.join([f.name for f in link.fields])

    @classmethod
    def _render_tree(cls, obj, breadcrumb=None):
        if breadcrumb is None:
            breadcrumb = []

        indent = '  ' * (len(breadcrumb))

        for key, link in obj.links.items():
            keys = breadcrumb + [key]
            yield '{key}: {link}'.format(
                indent=indent,
                key=key,
                link=cls.render_link(keys, link)
            )

        for key, sub_obj in obj.data.items():
            keys = breadcrumb + [key]
            yield '{key}: {{'.format(indent=indent, key=key)
            yield from [indent + '  ' + x for x in cls._render_tree(sub_obj, keys)]
            yield '},'

    @classmethod
    def render_tree(cls, doc):
        li = ['  ' + x for x in cls._render_tree(doc)]
        s = '\n'.join(li)

        return '{\n' + s + '\n}'

    def render(self, data, media_type=None, renderer_context=None):
        codec = coreapi.codecs.CoreJSONCodec()
        schema = base64.b64encode(codec.encode(data))

        template = loader.get_template(self.template)
        context = {
            'schema': mark_safe(schema),
            'api': mark_safe(self.render_tree(data)),
        }

        request = renderer_context['request']
        return template_render(template, context, request=request)
        # tree = {}
        # pass
        # return ''
