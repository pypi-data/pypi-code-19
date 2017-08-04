from django import template
from django.utils.safestring import mark_safe
from markdown import markdown

register = template.Library()


@register.tag(name='markdown')
def do_markdown(parser, token):
    nodelist = parser.parse(('endmarkdown',))
    parser.delete_first_token()
    return MarkdownNode(nodelist)


class MarkdownNode(template.Node):
    def __init__(self, nodelist):
        self.nodelist = nodelist

    def render(self, context):
        value = self.nodelist.render(context)
        return mark_safe(markdown(value))
