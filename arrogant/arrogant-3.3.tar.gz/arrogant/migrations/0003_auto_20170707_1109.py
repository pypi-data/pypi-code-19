# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-07-07 03:09
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('arrogant', '0002_job_available'),
    ]

    operations = [
        migrations.AlterField(
            model_name='job',
            name='name',
            field=models.CharField(default='', max_length=40),
        ),
    ]
