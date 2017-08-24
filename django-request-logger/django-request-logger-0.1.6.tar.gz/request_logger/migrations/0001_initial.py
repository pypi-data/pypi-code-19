# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='UserRequest',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('path', models.CharField(max_length=2047)),
                ('method', models.CharField(max_length=255)),
                ('scheme', models.CharField(max_length=255)),
                ('body', models.TextField()),
                ('content_length', models.CharField(max_length=255)),
                ('content_type', models.CharField(max_length=255)),
                ('http_accept', models.CharField(max_length=255)),
                ('http_accept_encoding', models.CharField(max_length=255)),
                ('http_accept_language', models.CharField(max_length=255)),
                ('http_host', models.CharField(max_length=255)),
                ('http_referer', models.CharField(max_length=2047)),
                ('http_user_agent', models.CharField(max_length=255)),
                ('remote_addr', models.CharField(max_length=255)),
                ('remote_host', models.CharField(max_length=255)),
                ('remote_user', models.CharField(max_length=255)),
                ('server_name', models.CharField(max_length=255)),
                ('server_port', models.CharField(max_length=255)),
                ('post_data', models.TextField()),
                ('get_data', models.TextField()),
                ('cookies', models.TextField()),
                ('encoding', models.CharField(max_length=255)),
                ('is_ajax', models.BooleanField()),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL, null=True)),
            ],
        ),
    ]
