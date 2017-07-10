from django.utils.encoding import smart_text
from rest_framework.utils import formatting


def get_modelview_description(model, html=False):
    description = model.__doc__ or ''
    description = formatting.dedent(smart_text(description))
    if html:
        return formatting.markup_description(description)
    return description
