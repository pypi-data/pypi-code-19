import base64

import coreapi
from django.template import Template
from django.utils.safestring import mark_safe
from rest_framework.compat import template_render
from rest_framework.renderers import BaseRenderer


class ApiJsRenderer(BaseRenderer):
    media_type = 'application/javascript'
    format = 'javascript'
    charset = 'utf-8'

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
        opts = []
        for field in link.fields:
            if field.required:
                li.append(field.name)
            else:
                opts.append(field.name)
        if opts:
            li.append(
                "{{{}}}".format(', '.join(opts))
            )

        return ', '.join(li)

    @classmethod
    def render_type_name(cls, schema):
        _type = schema[schema.rfind('.') + 1:schema.rfind("'")]
        strange_types = {
            "Integer": "int",
            "Enum": "String",
            "Any": "*"
        }
        return _type if _type not in strange_types else strange_types[_type]

    @classmethod
    def render_comments(cls, link):
        comments = []
        for field in link.fields:
            _type = cls.render_type_name(str(type(field.schema)))
            comments.append("* @param {{{_type}{required}}} {param_name} - {description}".format(
                _type=_type,
                required="" if field.required else "?",
                param_name=field.name,
                description=field.schema.description
            ))
        if comments:
            comments.insert(0, "/**")
            comments.append('*/')
        return comments

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
            yield from cls.render_comments(link)
            yield '{key}: {link}'.format(
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
        src = """\
            let codec = new coreapi.codecs.CoreJSONCodec();
            let schema = codec.decode(atob('{{ schema }}'));
            let api = {{ api }};
        """
        template = Template('\n'.join(line.strip() for line in src.splitlines()))
        context = {
            'schema': mark_safe(schema),
            'api': mark_safe(self.render_tree(data)),
        }

        request = renderer_context['request']
        return template_render(template, context, request=request)
