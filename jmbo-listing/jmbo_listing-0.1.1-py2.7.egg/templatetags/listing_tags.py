import types

from django import template

from listing.models import Listing
from listing.styles import LISTING_MAP

register = template.Library()


@register.filter(name="join_titles")
def join_titles(value, delimiter=", "):
    return delimiter.join([v.title for v in value])


@register.tag
def listing(parser, token):
    tokens = token.split_contents()
    length = len(tokens)

    if length < 2:
        raise template.TemplateSyntaxError(
            "listing tag requires at least argument slug or queryset"
        )

    slug_or_queryset = tokens[1]

    kwargs = {}
    for token in tokens[2:]:
        k, v = token.split("=")
        kwargs[k] = v

    return ListingNode(slug_or_queryset, **kwargs)


class ListingNode(template.Node):

    def __init__(self, slug_or_queryset, **kwargs):
        self.slug_or_queryset = template.Variable(slug_or_queryset)
        self.kwargs = kwargs

    def render(self, context, as_tile=False):
        slug_or_queryset = self.slug_or_queryset.resolve(context)

        if isinstance(slug_or_queryset, types.UnicodeType):
            try:
                obj = Listing.permitted.get(slug=slug_or_queryset)
            except Listing.DoesNotExist:
                return ""

        else:
            class ListingProxy:
                """Helper class emulating Listing API so AbstractBaseStyle
                works. Essentially a record class."""

                def __init__(self, queryset_permitted, **kwargs):
                    self.queryset_permitted = queryset_permitted
                    self.items_per_page = 0
                    for k, v in kwargs.items():
                        setattr(self, k, v)
                    if not hasattr(self, "id"):
                        setattr(self, "id", None)

            di = {}
            for k, v in self.kwargs.items():
                di[k] = template.Variable(v).resolve(context)
            obj = ListingProxy(slug_or_queryset, **di)

        return LISTING_MAP[obj.style](obj).render(context, as_tile=as_tile)


@register.tag
def get_listing_queryset(parser, token):
    """{% get_listing_queryset [slug] as [varname] %}"""
    try:
        tag_name, slug, dc, as_var = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError(
            "get_listing_queryset tag has syntax {% get_listing_items [slug] as [varname] %}"
        )
    return ListingQuerysetNode(slug, as_var)


class ListingQuerysetNode(template.Node):

    def __init__(self, slug, as_var):
        self.slug = template.Variable(slug)
        self.as_var = template.Variable(as_var)

    def render(self, context):
        slug = self.slug.resolve(context)
        as_var = self.as_var.resolve(context)
        try:
            obj = Listing.permitted.get(slug=slug)
            context[as_var] = obj.queryset(context["request"])
        except Listing.DoesNotExist:
            obj = None
            context[as_var] = None

        return ""
