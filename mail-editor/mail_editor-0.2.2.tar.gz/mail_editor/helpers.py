from django.template import loader
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

from .models import MailTemplate
from . import settings


def find_template(template_name, language=None, base_url=None):
    template, created = MailTemplate.objects.get_or_create(template_type=template_name, language=language, defaults={
        'subject': get_subject(template_name, base_url=base_url),
        'body': get_body(template_name, base_url=base_url)
    })

    return template


def get_subject(template_name, base_url=None):
    template_config = settings.TEMPLATES.get(template_name)
    if template_config:
        subject = template_config.get('subject_default')
        if subject:
            return subject

    if not base_url:
        base_url = settings.BASE_URL

    return _('Please fix this template')


def get_body(template_name, base_url=None):
    template_config = settings.TEMPLATES.get(template_name)
    default = _('Your content here...')
    if template_config:
        body = template_config.get('body_default')
        if body:
            default = body

    if not base_url:
        base_url = settings.BASE_URL

    template = loader.get_template('mail/_outer_table.html')
    return template.render({'base_url': base_url, 'default': mark_safe(default)}, None)
