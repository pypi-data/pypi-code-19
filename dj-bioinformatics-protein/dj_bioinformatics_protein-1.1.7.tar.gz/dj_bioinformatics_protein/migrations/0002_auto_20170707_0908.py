# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-07-07 09:08
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dj_bioinformatics_protein', '0001_initial_squashed_0006_auto_20170707_0908'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fasta',
            name='description',
            field=models.CharField(max_length=1000),
        ),
    ]
