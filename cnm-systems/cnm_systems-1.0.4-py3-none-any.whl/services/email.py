import emails
import re
from django.conf import settings
from ..models import EmailTemplate


class EmailService:
    mail_obj = {}
    html_content = ''
    template_layout = 'templates/email_templates/'
    template_file = template_layout + 'email_layout.html'
    email_config = {}
    name_from = ''
    email_from = ''
    name_to = ''
    email_to = ''

    def __init__(self, name_from, email_from, name_to, email_to):
        self.email_config = settings.EMAIL_CONFIGS
        self.name_from = name_from
        self.email_from = email_from
        self.name_to = name_to
        self.email_to = email_to

    def send(self):
        message = emails.html(
            html=self.html_content,
            subject=self.mail_obj['subject'],
            mail_from=(self.name_from, self.email_from)
        )
        sendmail = message.send(
            to=(self.name_to, self.email_to),
            smtp=self.email_config
        )
        return sendmail.status_code

    def render_content(self, **kwargs):
        for karg in kwargs:
            self.html_content = self.template_replace(karg, kwargs[karg])
        with open(self.template_file) as temp:
            self.html_content = temp.read().replace('{{ message }}', self.html_content)
        return self

    def get_content_by_name(self, email_name, layout_name=None):
        self.mail_obj = EmailTemplate.objects.values('layout_name', 'subject', 'message').get(name=email_name)
        if layout_name != None:
            self.template_file = self.template_layout + '{}.html'.format(layout_name)
        else:
            self.template_file = self.template_layout + '{}.html'.format(self.mail_obj['layout_name'])
        return self

    def template_replace(self, old, new):
        matchs = re.findall('{{(.*?)}}', self.mail_obj['message'], re.DOTALL)
        for s in matchs:
            if s.strip() == old:
                self.mail_obj['message'] = self.mail_obj['message'].replace('{{' + s + '}}', new)
        return self.mail_obj['message']
