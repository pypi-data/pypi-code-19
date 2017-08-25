import bleach

from django import template
from django.conf import settings
from django.core.urlresolvers import reverse
from django.utils.module_loading import import_string
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _
from markdown.extensions import Extension as BaseExtension
from thorson_wiki.markup import ThorsonMarkdown

register = template.Library()

@register.filter
def can_read(user, article):
    """
    Returns True if the given user has the necessary permissions to read the
    given article.
    """

    return article.can_read(user)

@register.filter
def can_edit(user, article):
    """
    Returns True if the given user has the necessary permissions to read the
    given article.
    """

    return article.can_edit(user)

@register.filter
def markdown(content, namespace_=None):
    """
    Converts a string of markdown text into HTML,
    """

    namespace = settings.THORSONWIKI_NAMESPACES.get(namespace_, {})

    extensions = namespace.get('md_extensions', [])
    configs = namespace.get('md_configs', {})

    md = ThorsonMarkdown(
        extensions=extensions,
        extensions_configs=configs,
        namespace=namespace,
        namespace_=namespace_,
    )

    content = content.strip()

    allowed_tags = namespace.get('allowed_tags', bleach.ALLOWED_TAGS)
    allowed_attrs = namespace.get('allowed_attrs', 
            bleach.ALLOWED_ATTRIBUTES)

    html = md.convert(content)

    return mark_safe(bleach.clean(html, tags=allowed_tags,
        attributes=allowed_attrs))

@register.tag(name='markdown')
def md2html(parser, token):

    content = parser.parse(('endmarkdown',))
    parser.delete_first_token()

    return MarkdownNode(content)

class MarkdownNode(template.Node):

    def __init__(self, content):

        self.content = content

    def render(self, context):

        namespace = context.get('namespace', None)
        namespace_ = context.get('namespace_', None)
        request = context.get('request', None)

        extensions = namespace.get('md_extensions', [])
        configs = namespace.get('md_configs', {})

        md = ThorsonMarkdown(
            extensions=extensions,
            extension_configs=configs,
            namespace=namespace,
            namespace_=namespace_,
            request=request
        )

        content = self.content.render(context).strip()

        allowed_tags = namespace.get('allowed_tags', bleach.ALLOWED_TAGS)
        allowed_attrs = namespace.get('allowed_attrs',
                bleach.ALLOWED_ATTRIBUTES)
        html = md.convert(content)

        return mark_safe(bleach.clean(html, tags=allowed_tags,
            attributes=allowed_attrs))
