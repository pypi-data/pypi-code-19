# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-03-06 09:54
from __future__ import unicode_literals

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models

import twitch_auth.fields


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='OAuth2AccessToken',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('token', models.TextField(help_text='access token (OAuth2)', verbose_name='token')),
                ('token_secret',
                 models.TextField(blank=True, help_text='refresh token (OAuth2)', verbose_name='token secret')),
                ('expires_at', models.DateTimeField(blank=True, null=True, verbose_name='expires at')),
            ],
            options={
                'verbose_name': 'oauth2 application token',
                'verbose_name_plural': 'oauth2 application tokens',
            },
        ),
        migrations.CreateModel(
            name='TwitchAccount',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uid', models.CharField(max_length=139, unique=True, verbose_name='uid')),
                ('extra_data', twitch_auth.fields.JSONField(default=dict, verbose_name='extra data')),
                (
                'user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'twitch account',
                'verbose_name_plural': 'twitch accounts',
            },
        ),
        migrations.AddField(
            model_name='oauth2accesstoken',
            name='account',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='twitch_auth.TwitchAccount'),
        ),
    ]
