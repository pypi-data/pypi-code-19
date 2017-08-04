from django.conf import settings
from django.utils.translation import pgettext_lazy

FLUENTCMS_BUTTON_STYLES = getattr(settings, 'FLUENTCMS_BUTTON_STYLES', (
    ('btn-default', pgettext_lazy("button-style", u"Default")),
    ('btn-primary', pgettext_lazy("button-style", u"Primary")),
    ('btn-success', pgettext_lazy("button-style", u"Success")),
    ('btn-info', pgettext_lazy("button-style", u"Info")),
    ('btn-warning', pgettext_lazy("button-style", u"Warning")),
    ('btn-danger', pgettext_lazy("button-style", u"Danger")),
    ('btn-link', pgettext_lazy("button-style", u"Link")),
))

FLUENTCMS_BUTTON_SIZES = getattr(settings, 'FLUENTCMS_BUTTON_SIZES', (
    ('', pgettext_lazy("button-size", u"Default")),
    ('btn-lg', pgettext_lazy("button-size", u"Large")),
    ('btn-sm', pgettext_lazy("button-size", u"Small")),
    ('btn-xs', pgettext_lazy("button-size", u"Extra Small")),
))
