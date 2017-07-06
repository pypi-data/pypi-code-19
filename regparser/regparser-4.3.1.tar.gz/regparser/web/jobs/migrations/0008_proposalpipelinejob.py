# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-08-19 04:42
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jobs', '0007_regulationfile_url'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProposalPipelineJob',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('clear_cache', models.BooleanField(default=False)),
                ('destination', models.URLField(default=b'http://localhost:8888/api', max_length=2000)),
                ('notification_email', models.EmailField(blank=b'True', max_length=254)),
                ('job_id', models.UUIDField(default=None, null=True)),
                ('use_uploaded_metadata', models.UUIDField(default=None, null=True)),
                ('use_uploaded_regulation', models.UUIDField(default=None, null=True)),
                ('parser_errors', models.TextField(blank=True)),
                ('regulation_url', models.URLField(blank=True, max_length=2000)),
                ('status', models.CharField(choices=[(b'received', b'received'), (b'in_progress', b'in_progress'), (b'failed', b'failed'), (b'complete', b'complete'), (b'complete_with_errors', b'complete_with_errors')], default=b'received', max_length=32)),
                ('url', models.URLField(blank=True, max_length=2000)),
                ('file_hexhash', models.CharField(max_length=32)),
                ('only_latest', models.BooleanField(default=True)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
