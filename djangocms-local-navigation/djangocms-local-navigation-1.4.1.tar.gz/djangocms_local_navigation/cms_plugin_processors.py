from collections import defaultdict

from django.utils import six
from django.utils.safestring import mark_safe, SafeText
from django.utils.text import slugify

from .conf import settings
from .utils import get_nav_elements, get_soup


def patch_elements(instance, placeholder, rendered_content, original_context):
    soup = get_soup(rendered_content)
    elements = get_nav_elements(soup)
    add_ids(elements, instance.id)
    if settings.NAV_ELEMENTS_CLASS:
        add_class(elements, settings.NAV_ELEMENTS_CLASS)

    if soup.body:
        text = ''.join(six.text_type(t) for t in soup.body)
    else:
        text = soup.contents

    # Depending on whether the original rendered_content was marked as safe,
    # return a safe string
    if isinstance(rendered_content, SafeText):
        return mark_safe(text)
    else:
        return text


def add_class(elements, class_name):
    for element in elements:
        element['class'] = element.get('class', []) + [class_name]


def add_ids(elements, prefix=''):
    """
    Add an HTML id attribute to the given list of tags. `text` is the input
    HTML that will be parsed to search for `tags`. The content of the id
    attribute is a slugified version of the tag content. Also a `prefix` can be
    added to the generated ids to avoid collisions (since ids are supposed to
    be unique). This can be used to pass the id of the current placeholder to
    make sure generated ids are unique between placeholders.

    No id will be added on elements that already have an id.

    >>> add_ids('<h2>Hello</h2><p>Paragraph</p><h2>World</h2>', ['h2'])
    '<h2 id="hello">Hello</h2><p>Paragraph</p><h2 id="world">World</h2>'

    >>> add_ids('<h2>Hello</h2><p>Paragraph</p><h2>World</h2>', ['h2'], '99')
    '<h2 id="hello-99">Hello</h2><p>Paragraph</p><h2 id="world-99">World</h2>'

    >>> add_ids('<h2>Hello</h2><p>Hello</p>', ['h2', 'p'])
    '<h2 id="hello">Hello</h2><p id="hello-1">Hello</p>'

    >>> add_ids('<h2>Hello</h2><p>Hello</p>', ['h2', 'p'], '99')
    '<h2 id="hello-99">Hello</h2><p id="hello-99-1">Hello</p>'
    """
    existing_slugs = defaultdict(int)

    for element in elements:
        slug = slugify(element.string)

        # Only set the id if there's not already an id
        if 'id' not in element.attrs:
            element['id'] = '{slug}{prefix}{suffix}'.format(
                slug=slug,
                prefix='-{}'.format(prefix) if prefix else '',
                suffix='-{}'.format(existing_slugs[slug]) if slug in existing_slugs else ''
            )

        existing_slugs[slug] += 1

    return elements
