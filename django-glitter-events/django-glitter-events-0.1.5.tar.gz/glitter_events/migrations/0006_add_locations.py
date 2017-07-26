# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('glitter_events', '0005_rename_location_to_address'),
    ]

    operations = [
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=32, db_index=True)),
                ('slug', models.SlugField(unique=True, max_length=32)),
                ('location', models.CharField(unique=True, max_length=128)),
            ],
            options={
                'ordering': ('title',),
            },
        ),
        migrations.AddField(
            model_name='event',
            name='locations',
            field=models.ManyToManyField(to='glitter_events.Location', blank=True),
        ),
    ]
