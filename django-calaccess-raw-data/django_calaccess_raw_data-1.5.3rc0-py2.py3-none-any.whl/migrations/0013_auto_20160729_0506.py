# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-07-29 05:06
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('calaccess_raw', '0012_auto_20160728_1945'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='rawdataversion',
            options={'ordering': ('-release_datetime',), 'verbose_name': 'CAL-ACCESS raw data version'},
        ),
    ]
