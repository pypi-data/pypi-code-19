import os
import glob
from django.conf import settings
from datetime import datetime
from django.db import models
from django.utils.translation import gettext_lazy as _
from tinymce.models import HTMLField
from ckeditor.fields import RichTextField


class Logs(models.Model):
    TYPE_CHOICES = (
        ('log', 'Log'),
        ('info', 'Info'),
        ('exception', 'Exception'),
        ('error', 'Error'),
    )
    log_name = models.CharField(max_length=255)
    log_level = models.CharField(max_length=50, null=False, default='log', choices=TYPE_CHOICES)
    log_msg = models.TextField()
    created_at = models.DateTimeField(default=datetime.now, blank=True)

    def __str__(self):
        return self.log_name

    def _log_msg(self):
        return self.log_msg

    def _log_level(self):
        return self.log_level

    _log_msg.allow_tags = True  # set this to not HTML-escape the output
    _log_msg.short_description = 'Message'
    _log_level.short_description = 'Level'

    class Meta:
        db_table = "logs"
        verbose_name = _('log')
        verbose_name_plural = _('logs')


class EmailTemplate(models.Model):
    path = settings.TEMPLATES[0]['DIRS'][0]
    folder = path + '\\email_templates\\*'
    template_files = [os.path.basename(x) for x in glob.glob(folder)]
    LAYOUT_CHOICES = [
        ('email_layout', 'email_layout'),
    ]
    for file in template_files:
        name = os.path.splitext(file)[0]
        LAYOUT_CHOICES.append((name, name,))

    layout_name = models.CharField(max_length=255, null=False, default='email_layout', choices=LAYOUT_CHOICES)
    name = models.CharField(max_length=255, unique=True)
    subject = models.CharField(max_length=255)
    if settings.CNM_CONFIGS['editor'].lower() == 'ckeditor':
        message = RichTextField(config_name="default")
    else:
        message = models.TextField()

    def _message(self):
        return self.message

    _message.allow_tags = True  # set this to not HTML-escape the output
    _message.short_description = 'Message'

    def __str__(self):
        return self.subject

    class Meta:
        db_table = "email_templates"



class SysProcess(models.Model):
    content_id = models.IntegerField()
    content_type = models.CharField(max_length=50)
    priority = models.IntegerField()
    status = models.IntegerField(default=0)
    created_at = models.DateTimeField(default=datetime.now, blank=True)

    class Meta:
        db_table = "sys_process"
        verbose_name = _('process')
        verbose_name_plural = _('processes')
