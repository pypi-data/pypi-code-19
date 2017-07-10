from django import template


register = template.Library()

@register.simple_tag
def pages_relative(page_obj, delta=3):
    from_page = max(page_obj.number - delta, 1) - 1
    to_page = min(page_obj.number + delta, page_obj.paginator.num_pages)
    relative_range = page_obj.paginator.page_range[from_page:to_page]
    return relative_range

@register.simple_tag(takes_context=True)
def page_url(context, page):
    request = context['request']
    args = {}
    for key, value in request.GET.items():
        args[key] = value[0] if isinstance(value, (list, tuple)) else value
    args['page'] = page
    return '?' + '&'.join('{0}={1}'.format(key, value) for key, value in args.items())
