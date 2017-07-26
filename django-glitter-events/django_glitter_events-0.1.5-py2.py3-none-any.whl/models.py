# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from taggit.managers import TaggableManager

from django.core.urlresolvers import reverse
from django.db import models
from django.utils.encoding import python_2_unicode_compatible

from glitter.assets.fields import AssetForeignKey
from glitter.mixins import GlitterMixin
from glitter.models import BaseBlock


@python_2_unicode_compatible
class Category(models.Model):
    title = models.CharField(max_length=100, db_index=True)
    slug = models.SlugField(max_length=100, unique=True)

    class Meta:
        ordering = ('title',)
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('glitter-events:category-event-list', kwargs={
            'slug': self.slug,
        })


@python_2_unicode_compatible
class Location(models.Model):
    title = models.CharField(max_length=32, db_index=True)
    slug = models.SlugField(max_length=32, unique=True)
    location = models.CharField(max_length=128, unique=True)

    class Meta:
        ordering = ('title',)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('glitter-events:location-event-list', kwargs={
            'slug': self.slug,
        })


@python_2_unicode_compatible
class Event(GlitterMixin):
    category = models.ForeignKey('glitter_events.Category')
    title = models.CharField(max_length=100, db_index=True)
    slug = models.SlugField(max_length=100, unique_for_date='start')
    address = models.CharField(max_length=128, blank=True)
    locations = models.ManyToManyField(Location, blank=True)
    image = AssetForeignKey('glitter_assets.Image', null=True, blank=True)
    summary = models.TextField(help_text='A short sentence description of the event.')
    start = models.DateTimeField(help_text='Start time/date.')
    end = models.DateTimeField(help_text='End time/date.', blank=True, null=True)
    date_url = models.DateField(db_index=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    tags = TaggableManager(blank=True)

    class Meta(GlitterMixin.Meta):
        ordering = ('start',)

    def __str__(self):
        out = '{start} - {title}'.format(
            start=self.start.strftime('%Y-%m-%d - %I:%M%p'), title=self.title
        )
        return out

    def save(self, *args, **kwargs):
        self.date_url = self.start.date()
        super(Event, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('glitter-events:detail', kwargs={
            'year': self.date_url.year,
            'month': str(self.date_url.month).zfill(2),
            'day': str(self.date_url.day).zfill(2),
            'slug': self.slug,
        })


class UpcomingEventsBlock(BaseBlock):
    category = models.ForeignKey(
        'glitter_events.Category', null=True, blank=True, on_delete=models.PROTECT
    )
    tags = models.CharField(max_length=255, blank=True)

    class Meta:
        verbose_name = 'upcoming events'
