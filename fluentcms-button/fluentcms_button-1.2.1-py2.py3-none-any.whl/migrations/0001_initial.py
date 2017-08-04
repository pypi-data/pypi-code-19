# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from fluentcms_button import appsettings
import fluent_contents.extensions


class Migration(migrations.Migration):

    dependencies = [
        ('fluent_contents', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ButtonItem',
            fields=[
                ('contentitem_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='fluent_contents.ContentItem')),
                ('title', models.CharField(max_length=200, verbose_name='Title')),
                ('url', fluent_contents.extensions.PluginUrlField(max_length=300, verbose_name='URL')),
                ('style', models.CharField(max_length=50, verbose_name='Style', choices=appsettings.FLUENTCMS_BUTTON_STYLES)),
                ('size', models.CharField(default='', max_length=10, verbose_name='Size', blank=True, choices=appsettings.FLUENTCMS_BUTTON_SIZES)),
                ('block', models.BooleanField(default=False, verbose_name='Span the full width')),
            ],
            options={
                'db_table': 'contentitem_fluentcms_button_buttonitem',
                'verbose_name': 'Button',
                'verbose_name_plural': 'Button',
            },
            bases=('fluent_contents.contentitem',),
        ),
    ]
