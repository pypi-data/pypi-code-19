import logging
import os
import warnings

from django.conf import settings as django_settings
from django.core.mail import EmailMultiAlternatives
from django.db import models
from django.db.models import Q
from django.template import Context, Template, loader
from django.utils.encoding import python_2_unicode_compatible
from django.utils.html import strip_tags
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from premailer import Premailer

from . import settings
from .mail_template import validate_template
from .utils import variable_help_text


logger = logging.getLogger(__name__)


class MailTemplateManager(models.Manager):
    def get_for_language(self, template_type, language):
        """
        Returns the `MailTemplate` for the given type in the given language. If the language does not exist, it
        attempts to find and return the fallback (no language) instance.

        :param template_type:
        :param language:
        :return:
        """
        mail_template = self.filter(
            template_type=template_type
        ).filter(
            Q(language=language)|Q(language='')
        ).order_by('-language').first()
        if mail_template is None:
            raise MailTemplate.DoesNotExist()
        return mail_template


@python_2_unicode_compatible
class MailTemplate(models.Model):
    template_type = models.CharField(_('type'), max_length=50)
    language = models.CharField(max_length=10, choices=django_settings.LANGUAGES, blank=True)

    remarks = models.TextField(_('remarks'), blank=True, default='', help_text=_('Extra information about the template'))
    subject = models.CharField(_('subject'), max_length=255)
    body = models.TextField(_('body'), help_text=_('Add the body with {{variable}} placeholders'))

    objects = MailTemplateManager()

    CONFIG = {}
    CHOICES = None

    class Meta:
        verbose_name = _('mail template')
        verbose_name_plural = _('mail templates')
        unique_together = (('template_type', 'language'), )

    def __init__(self, *args, **kwargs):
        super(MailTemplate, self).__init__(*args, **kwargs)
        self.CONFIG = settings.get_config()

    def __str__(self):
        return self.template_type

    def clean(self):
        validate_template(self)

    def render_subject(self, context):
        return Template(self.subject).render(Context(context, autoescape=False))

    def render_body(self, context):
        # Render the body template
        partial_body = Template(self.body).render(Context(context))
        base_url = context.get('base_url', settings.BASE_URL)
        # Surround the rendered body template with the base layout.
        template = loader.get_template('mail/_base.html')
        body = template.render({'base_url': base_url, 'content': partial_body}, None)

        # Transform any styles into inline styles.
        body = Premailer(body, base_url=base_url).transform()

        return mark_safe(body)

    def build_mail(self, from_email=None, to=None, bcc=None, connection=None, attachments=None,
                   headers=None, alternatives=None, cc=None, reply_to=None, context=None):
        """
        Render this template body and subject, using the passed `context`, to construct the mail.

        :param from_email:
        :param to:
        :param bcc:
        :param connection:
        :param attachments:
        :param headers:
        :param alternatives:
        :param cc:
        :param reply_to:
        :param body_context:
        :return:
        """
        if context is None:
            context = {}

        subject = self.render_subject(context)
        html_body = self.render_body(context)
        text_body = strip_tags(html_body)

        email_message = EmailMultiAlternatives(
            subject=subject,
            body=text_body,
            from_email=from_email,
            to=to,
            bcc=bcc,
            connection=None,
            attachments=attachments,
            headers=headers,
            alternatives=alternatives,
            cc=cc,
            reply_to=reply_to,
        )
        email_message.attach_alternative(html_body, 'text/html')
        return email_message

    def send_mail(self, from_email=None, to=None, bcc=None,
                  connection=None, attachments=None, headers=None, alternatives=None,
                  cc=None, reply_to=None, context=None):
        """
        Render this template body and subject, using the passed `context`, to construct the mail and send it.

        :param from_email:
        :param to:
        :param bcc:
        :param connection:
        :param attachments:
        :param headers:
        :param alternatives:
        :param cc:
        :param reply_to:
        :param body_context:
        :return:
        """
        email_message = self.build_mail(
            from_email=from_email, to=to, bcc=bcc, connection=connection, attachments=attachments,
            headers=headers, alternatives=alternatives, cc=cc, reply_to=reply_to, context=context
        )
        return email_message.send()

    def send_email(self, to_addresses, context, subj_context=None, txt=False, attachments=None):
        """
        You can pass the context only. We will pass the context to the subject context when we don't
        have a subject context.

        @param attachments: List of tuples, where the tuple can be one of two forms:
                            `(<absolute file path>, [mime type])` or
                            `(<filename>, <content>, [mime type])`
        """
        warnings.warn(
            'MailTemplate.send_email() is deprecated in favor of MailTemplate.send_mail() which has all the parameters'
            'from Django\'s EmailMultiAlternatives constructor.',
            DeprecationWarning
        )

        subject, body = self.render_body(context), self.render_subject(subj_context or context)
        text_body = txt or strip_tags(body)

        email_message = EmailMultiAlternatives(subject=subject, body=text_body, from_email=django_settings.DEFAULT_FROM_EMAIL, to=to_addresses)
        email_message.attach_alternative(body, 'text/html')

        if attachments:
            for attachment in attachments:
                if not attachment or not isinstance(attachment, tuple):
                    raise ValueError('Attachments should be passed as a list of tuples.')
                if os.path.isabs(attachment[0]):
                    email_message.attach_file(*attachment)
                else:
                    email_message.attach(*attachment)

        return email_message.send()

    def get_variable_help_text(self):
        return variable_help_text(self.template_type)
