from django_jinja import library

from configfactory.forms import html_params


@library.global_function
def render_attrs(**params):
    return html_params(**params)
