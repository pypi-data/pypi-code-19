from django import template
from django.utils.safestring import mark_safe
from django.conf import settings

register = template.Library()


def get_url(url_name, *args, **kwargs):
    from django.urls import reverse, NoReverseMatch
    try:
        _link = reverse(url_name, args=args, kwargs=kwargs)
    except NoReverseMatch:
        return '#unknown-url'


@register.filter
def replace(value, arg):
    pair = arg.split(',')
    if len(pair) == 1:
        pair.append('')
    return value.replace(*pair)


@register.filter
def replace_alt(value, arg):
    pair = arg.split(':')
    if len(pair) == 1:
        pair.append('')
    return value.replace(*pair)


@register.filter
def asset_url(value):
    from django.contrib.staticfiles.templatetags.staticfiles import static
    chunks = value.split('?')
    result = static('assets/%s' % chunks[0])
    if len(chunks) > 1:
        result += '?%s' % chunks[1]
    return mark_safe(result)


@register.filter
def templated_asset_url(value):
    from django.urls import reverse
    return mark_safe(reverse('render_asset', args=[value]))


@register.filter
def stylesheet_tag(value):
    return mark_safe('<link href="%s" rel="stylesheet">' % value)


@register.filter
def script_tag(value):
    return mark_safe('<script src="%s" type="text/javascript"></script>' % value)


@register.filter
def shopify_asset_url(value):
    return mark_safe('<script src="//cdn.shopify.com/s/shopify/%s" type="text/javascript"></script>' % value)


@register.filter
def handle(value):
    from pcart_core.utils import slugify_unicode
    return slugify_unicode(value)


@register.filter
def img_tag(value, arg=''):
    _chunks = arg.split(',')
    _extra = ''
    if _chunks:
        _extra += ' alt="%s"' % _chunks[0]
        if len(_chunks) > 1:
            _extra += ' class="%s"' % _chunks[1]
    return '<img src="%s" %s>' % (value, _extra)


@register.filter
def link_to(label, url):
    return mark_safe('<a href="%s">%s</a>' % (url, label))


@register.filter
def customer_logout_link(label):
    return '<a href="%s">%s</a>' % (get_url('logout'), label)


@register.filter
def customer_register_link(label):
    return '<a href="%s">%s</a>' % (get_url('register'), label)


@register.filter
def customer_login_link(label):
    return '<a href="%s">%s</a>' % (get_url('login'), label)


@register.filter
def limit(sequence, limit):
    if sequence is None:
        return None
    else:
        return sequence[:limit]


@register.filter
def offset(sequence, offset):
    return sequence[offset:]


@register.filter(name='slice')
def _slice(sequence, arg):
    if type(arg) is int:
        return sequence[arg]
    elif type(arg) is str:
        _chunks = arg.split(',')
        return sequence[int(_chunks[0]):int(_chunks[0])+int(_chunks[1])]


@register.filter
def plus(value, arg):
    if value is None:
        return arg
    elif type(value) is str and type(arg) is int:
        return int(value) + arg
    elif type(value) is int and type(arg) is str:
        return value + int(arg)
    else:
        return value + arg


@register.filter
def minus(value, arg):
    if value is None:
        return arg
    elif type(value) is str and type(arg) is int:
        return int(value) - arg
    elif type(value) is int and type(arg) is str:
        return value - int(arg)
    else:
        return value - arg


@register.filter
def remove(value, arg):
    return value.replace(arg, '')


@register.filter
def divided_by(value, arg):
    if type(value) is str and type(arg) is int:
        return int(value) / arg
    elif type(value) is int and type(arg) is str:
        return value / int(arg)
    else:
        return value / arg


@register.filter
def modulo(value, arg):
    if type(value) is str and type(arg) is int:
        return int(value) % arg
    elif type(value) is int and type(arg) is str:
        return value % int(arg)
    else:
        return value % arg


@register.filter
def times(value, arg):
    if type(value) is str and type(arg) is int:
        return int(value) * arg
    elif type(value) is int and type(arg) is str:
        return value * int(arg)
    else:
        return value * arg


@register.filter(name='range')
def _range(value):
    chunks = value.split(',')
    if len(chunks) == 1:
        return range(int(chunks[0]))
    elif len(chunks) > 1:
        return range(int(chunks[0]), int(chunks[1]))


@register.filter(name='attr')
def _attr(obj, attr):
    return getattr(obj, attr)


@register.filter(name='element')
def _element(obj, element):
    if obj is None:
        return None
    elif obj == '':
        return ''
    else:
        return obj.get(element)


@register.filter(name='json')
def _json(value):
    import json
    return mark_safe(json.dumps(value))


@register.filter(name='split')
def _split(value, delimiter=','):
    return value.split(delimiter)


@register.filter(name='last')
def _last(sequence):
    return sequence[-1]


@register.filter(name='first')
def _first(sequence):
    return sequence[0]


@register.simple_tag(takes_context=True)
def get_template_name(context):
    return context.template.name


@register.tag(name='capture')
def do_capture(parser, token):
    """
    Capture the contents of a tag output.
    Usage:
    .. code-block:: html+django
        {% capture %}..{% endcapture %}                    # output in {{ capture }}
        {% capture silent %}..{% endcapture %}             # output in {{ capture }} only
        {% capture as varname %}..{% endcapture %}         # output in {{ varname }}
        {% capture as varname silent %}..{% endcapture %}  # output in {{ varname }} only
    For example:
    .. code-block:: html+django
        {# Allow templates to override the page title/description #}
        <meta name="description" content="{% capture as meta_description %}{% block meta-description %}{% endblock %}{% endcapture %}" />
        <title>{% capture as meta_title %}{% block meta-title %}Untitled{% endblock %}{% endcapture %}</title>
        {# copy the values to the Social Media meta tags #}
        <meta property="og:description" content="{% block og-description %}{{ meta_description }}{% endblock %}" />
        <meta name="twitter:title" content="{% block twitter-title %}{{ meta_title }}{% endblock %}" />
    """
    bits = token.split_contents()

    # tokens
    t_as = 'as'
    t_silent = 'silent'
    var = 'capture'
    silent = False

    num_bits = len(bits)
    if len(bits) > 4:
        raise template.TemplateSyntaxError("'capture' node supports '[as variable] [silent]' parameters.")
    elif num_bits == 4:
        t_name, t_as, var, t_silent = bits
        silent = True
    elif num_bits == 3:
        t_name, t_as, var = bits
    elif num_bits == 2:
        t_name, t_silent = bits
        silent = True
    else:
        var = 'capture'
        silent = False

    if t_silent != 'silent' or t_as != 'as':
        raise template.TemplateSyntaxError("'capture' node expects 'as variable' or 'silent' syntax.")

    nodelist = parser.parse(('endcapture',))
    parser.delete_first_token()
    return CaptureNode(nodelist, var, silent)


class CaptureNode(template.Node):
    def __init__(self, nodelist, varname, silent):
        self.nodelist = nodelist
        self.varname = varname
        self.silent = silent

    def render(self, context):
        output = self.nodelist.render(context)
        context[self.varname] = output
        if self.silent:
            return ''
        else:
            return output
