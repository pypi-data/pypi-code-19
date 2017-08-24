from django import template
from django.forms import widgets
from django.template import Context
from django.template.loader import get_template

FSFIELD_TEMPLATE_PATH = 'fsforms/field.html'

register = template.Library()


def is_checkbox(field):
    return isinstance(field.field.widget, widgets.CheckboxInput)


def is_list_choices(field):
    return (isinstance(field.field.widget, widgets.ChoiceWidget) and
            field.field.widget.input_type in ['checkbox', 'radio'])


@register.filter(name='fsfield')
def fsfield_filter(field):
    """
    Renders a form field with Foundation Forms structure::

        {{ form.my_field|fsfield }}

    Use the ``fsfield`` tag if you want to tun up the output.
    """
    template = get_template(FSFIELD_TEMPLATE_PATH)
    c = Context(_fsfield_context(field)).flatten()
    return template.render(c)


@register.inclusion_tag(FSFIELD_TEMPLATE_PATH, name='fsfield')
def fsfield_tag(field, label_class='', show_errors=True, as_list=False,
                **attrs):
    """
    Renders a form field with Foundation Forms structure.

    Besides the field, it takes some arguments to customize its rendering.
    The `̀`label_class`` argument contains additional CSS class to apply to the
    label element. Note that if ``show_errors`` is ``True``, the error classes
    will be automatically added. Otherwise, the field errors will not be
    displayed.
    The choices widgets - i.e. RadioSelect and CheckboxSelectMultiple - will
    be rendered inline and wrapped in a fieldset by default. If ``as_list`` is
    ``True``, they will be rendered as a list instead - as the Django's default
    behavior.
    Finally, all the remaining arguments will be added to the widget attributes.

    Sample usage::

        {% fsfield form.my_field label_class="my-field" %}
    """
    if field.is_hidden:
        return {'field': field}

    # alter the field's required value
    if 'required' in attrs:
        field.field.required = attrs.pop('required')

    widget = field.field.widget

    # set remaining arguments as attributes of the widget
    for name, value in attrs.items():
        if name in widget.attrs:
            widget.attrs[name] += ' ' + value
        else:
            widget.attrs[name] = value

    return _fsfield_context(field, label_class, show_errors, as_list)


def _fsfield_context(field, label_class='', show_errors=True, as_list=False):
    """Constructs the context for the fsforms/field.html template."""
    widget = field.field.widget
    field_id = widget.attrs.get('id') or field.auto_id

    # set error CSS classes
    if show_errors and field.errors:
        label_class = ('is-invalid-label ' + label_class).strip()
        widget.attrs['class'] = (
            'is-invalid-input ' + widget.attrs.get('class', '')
        ).strip()

    # add the accessibility attribute
    if field.help_text:
        widget.attrs['aria-describedby'] = 'helptext_' + field_id

    return {
        'field': field,
        'field_id': field_id,
        'as_list': as_list,
        'show_errors': show_errors,
        'label_class': label_class,
        'is_checkbox': is_checkbox(field),
        'is_list_choices': is_list_choices(field),
    }
