# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import filer.fields.folder
import django.db.models.deletion
import filer.fields.image
import aldryn_lightslider.models


class Migration(migrations.Migration):

    dependencies = [
        ('cms', '0016_auto_20160608_1535'),
        ('filer', '0006_auto_20160623_1627'),
    ]

    operations = [
        migrations.CreateModel(
            name='LightsliderPlugin',
            fields=[
                ('cmsplugin_ptr', models.OneToOneField(parent_link=True, related_name='+', primary_key=True, serialize=False, to='cms.CMSPlugin')),
                ('number_of_concurrent_slides', models.PositiveIntegerField(default=3, help_text='How many images displayed at the same time.', verbose_name='Number of concurrent slides')),
                ('number_of_paginating_slides', models.PositiveIntegerField(default=1, help_text='How many images to slide out when going forward or backward.', verbose_name='Number of paginating slides')),
                ('style', models.CharField(default=b'standard', max_length=50, verbose_name='Style', choices=[(b'standard', 'Standard')])),
                ('aspect_ratio', models.CharField(default=b'', max_length=10, verbose_name='aspect ratio', blank=True, choices=[('1x1', '1x1'), ('4x3', '4x3'), ('16x9', '16x9'), ('16x10', '16x10'), ('21x9', '21x9'), ('3x4', '3x4'), ('9x16', '9x16'), ('10x16', '10x16'), ('9x21', '9x21')])),
                ('transition_effect', models.CharField(default=b'', max_length=50, verbose_name='Transition Effect', blank=True, choices=[(b'slide', 'Slide')])),
                ('ride', models.BooleanField(default=True, help_text='Whether to mark the carousel as animating starting at page load.', verbose_name='Ride')),
                ('interval', models.IntegerField(default=5000, help_text='The amount of time to delay between automatically cycling an item.', verbose_name='Interval')),
                ('wrap', models.BooleanField(default=True, help_text='Whether the carousel should cycle continuously or have hard stops.')),
                ('pause', models.BooleanField(default=True, help_text='Pauses the cycling of the carousel on mouseenter and resumes the cycling of the carousel on mouseleave.')),
                ('classes', aldryn_lightslider.models.Classes(default=b'', help_text=b'space separated classes that are added to the class. see <a href="http://getbootstrap.com/css/" target="_blank">bootstrap docs</a>', blank=True)),
            ],
            options={
                'abstract': False,
            },
            bases=('cms.cmsplugin',),
        ),
        migrations.CreateModel(
            name='LightsliderSlideFolderPlugin',
            fields=[
                ('cmsplugin_ptr', models.OneToOneField(parent_link=True, related_name='+', primary_key=True, serialize=False, to='cms.CMSPlugin')),
                ('classes', aldryn_lightslider.models.Classes(default=b'', help_text=b'space separated classes that are added to the class. see <a href="http://getbootstrap.com/css/" target="_blank">bootstrap docs</a>', blank=True)),
                ('folder', filer.fields.folder.FilerFolderField(verbose_name='folder', to='filer.Folder')),
            ],
            options={
                'abstract': False,
            },
            bases=('cms.cmsplugin',),
        ),
        migrations.CreateModel(
            name='LightsliderSlidePlugin',
            fields=[
                ('cmsplugin_ptr', models.OneToOneField(parent_link=True, related_name='+', primary_key=True, serialize=False, to='cms.CMSPlugin')),
                ('title', models.CharField(max_length=100, verbose_name='title', blank=True)),
                ('classes', aldryn_lightslider.models.Classes(default=b'', help_text=b'space separated classes that are added to the class. see <a href="http://getbootstrap.com/css/" target="_blank">bootstrap docs</a>', blank=True)),
                ('image', filer.fields.image.FilerImageField(related_name='+', on_delete=django.db.models.deletion.SET_NULL, verbose_name='image', to='filer.Image', null=True)),
            ],
            options={
                'abstract': False,
            },
            bases=('cms.cmsplugin',),
        ),
    ]
