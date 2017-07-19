# -*- coding: utf-8 -*-

from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from django.db import models

from model_utils.models import TimeStampedModel, TimeFramedModel


class Overview(TimeStampedModel):
    user = models.ForeignKey(User)
    text = models.TextField()

    class Meta:
        verbose_name_plural = "Overview"

    def __unicode__(self):
        return self.text[0:40] + '...'


class PersonalSocialMedia(TimeStampedModel):
    user = models.ForeignKey(User)
    linkedin = models.CharField(max_length=255, null=True, blank=True)
    twitter = models.CharField(max_length=255, null=True, blank=True)
    github = models.CharField(max_length=255, null=True, blank=True)
    bitbucket = models.CharField(max_length=255, null=True, blank=True)
    gitlab = models.CharField(max_length=255, null=True, blank=True)
    gplus = models.CharField(max_length=255, null=True, blank=True)
    instagram = models.CharField(max_length=255, null=True, blank=True)
    snapchat = models.CharField(max_length=255, null=True, blank=True)
    skype = models.CharField(max_length=255, null=True, blank=True)
    wordpress = models.URLField(_('wordpress'), blank=True)
    youtube = models.URLField(_('youtube'), blank=True)

    def __unicode__(self):
        return self.person


class PersonalPhone(TimeStampedModel):
    user = models.ForeignKey(User)
    name = models.CharField(max_length=255)
    phone = models.IntegerField(blank=True)

    def __unicode__(self):
        return "{} ({})".format(self.person, self.name)


class EducationInfo(TimeStampedModel, TimeFramedModel):
    user = models.ForeignKey(User)
    name = models.CharField(max_length=250)
    location = models.CharField(max_length=250)
    school_url = models.URLField(_('School URL'))
    summary = models.TextField()
    is_current = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = "Education"

    def edu_date_range(self):
        return ''.join(['(', self.formatted_start_date(),
                        '-', self.formatted_end_date(), ')'])

    def full_start_date(self):
        return self.start.strftime("%Y-%m-%d")

    def full_end_date(self):
        if self.is_current:
            return time.strftime("%Y-%m-%d", time.localtime())
        else:
            return self.end.strftime("%Y-%m-%d")

    def formatted_start_date(self):
        return self.start.strftime("%b %Y")

    def formatted_end_date(self):
        if self.is_current:
            return _("Current")
        else:
            return self.end.strftime("%b %Y")

    def __unicode__(self):
        return ' '.join([self.name, self.edu_date_range()])


class JobInfo(TimeStampedModel, TimeFramedModel):
    user = models.ForeignKey(User)
    company = models.CharField(max_length=250)
    location = models.CharField(max_length=250)
    title = models.CharField(max_length=250)
    company_url = models.URLField(_('Company URL'))
    description = models.TextField(blank=True)
    is_current = models.BooleanField(default=False)
    is_public = models.BooleanField(default=True)
    company_image = models.CharField(max_length=250, blank=True,
                                     help_text=_('Path to company image, '
                                                 'local or otherwise'))

    class Meta:
        db_table = 'jobs'
        ordering = ['-end', '-start']

    def job_date_range(self):
        return ''.join(['(', self.formatted_start_date(),
                        '-', self.formatted_end_date(), ')'])

    def full_start_date(self):
        return self.start.strftime("%Y-%m-%d")

    def full_end_date(self):
        if self.is_current:
            return time.strftime("%Y-%m-%d", time.localtime())
        else:
            return self.end.strftime("%Y-%m-%d")

    def formatted_start_date(self):
        return self.start.strftime("%b %Y")

    def formatted_end_date(self):
        if self.is_current:
            return _("Current")
        else:
            return self.end.strftime("%b %Y")

    def __unicode__(self):
        return ' '.join([self.company, self.job_date_range()])


class Accomplishment(TimeStampedModel):
    job = models.ForeignKey(JobInfo)
    description = models.TextField()
    order = models.IntegerField(default=0)

    class Meta:
        db_table = 'accomplishments'
        ordering = ['order']

    def __unicode__(self):
        return ''.join([self.job.company, '-', self.description[0:50], '...'])


class Skillset(TimeStampedModel):
    name = models.CharField(max_length=250)

    def __unicode__(self):
        return self.name


class Skill(TimeStampedModel):
    user = models.ForeignKey(User)
    name = models.CharField(max_length=250)
    skill_url = models.URLField(_('Skill URL'), blank=True)
    skillset = models.ForeignKey(Skillset)

    class Meta:
        ordering = ['id']

    def __unicode__(self):
        return ''.join([self.skillset.name, '-', self.name])


class Language(TimeStampedModel):
    name = models.CharField(max_length=250)

    def __unicode__(self):
        return self.name


class LanguageInfo(TimeStampedModel):
    user = models.ForeignKey(User)
    language = models.ForeignKey(Language)
    level = models.CharField(max_length=250)

    def __unicode__(self):
        return ' - '.join([self.user, self.language])
