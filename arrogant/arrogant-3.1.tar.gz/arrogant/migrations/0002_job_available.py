# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-07-02 08:01
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('arrogant', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='job',
            name='available',
            field=models.BooleanField(default=False),
        ),
    ]
