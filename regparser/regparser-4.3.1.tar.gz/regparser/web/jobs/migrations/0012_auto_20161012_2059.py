# -*- coding: utf-8 -*-
# Generated by Django 1.9.10 on 2016-10-12 20:59
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jobs', '0011_auto_20161011_2135'),
    ]

    operations = [
        migrations.AlterField(
            model_name='regulationfile',
            name='hexhash',
            field=models.CharField(max_length=64, primary_key=True, serialize=False),
        ),
    ]
