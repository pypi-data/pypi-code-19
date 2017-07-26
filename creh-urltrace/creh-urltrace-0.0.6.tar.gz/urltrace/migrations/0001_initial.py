# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='UrlTrace',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('url_trace', models.TextField(unique=True)),
                ('description', models.TextField(blank=True)),
                ('is_active', models.SmallIntegerField(default=1, choices=[(1, b'True'), (2, b'False')])),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, editable=False)),
                ('updated_at', models.DateTimeField(default=django.utils.timezone.now, editable=False)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='UrlTraceGroup',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('group_name', models.TextField(unique=True)),
                ('description', models.TextField(blank=True)),
                ('is_active', models.SmallIntegerField(default=1, choices=[(1, b'True'), (2, b'False')])),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, editable=False)),
                ('updated_at', models.DateTimeField(default=django.utils.timezone.now, editable=False)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='urltrace',
            name='url_trace_group',
            field=models.ForeignKey(to='urltrace.UrlTraceGroup'),
            preserve_default=True,
        ),
    ]
