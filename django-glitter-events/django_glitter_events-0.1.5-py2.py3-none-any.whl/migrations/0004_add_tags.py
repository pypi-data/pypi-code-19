# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import taggit.managers


class Migration(migrations.Migration):

    dependencies = [
        ('taggit', '0002_auto_20150616_2121'),
        ('glitter_events', '0003_optional_end'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='tags',
            field=taggit.managers.TaggableManager(to='taggit.Tag', verbose_name='Tags', blank=True, through='taggit.TaggedItem', help_text='A comma-separated list of tags.'),
        ),
        migrations.AddField(
            model_name='upcomingeventsblock',
            name='tags',
            field=models.CharField(blank=True, max_length=255),
        ),
    ]
