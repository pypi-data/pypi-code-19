# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-06-07 11:14
from __future__ import unicode_literals

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('aa_stripe', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='stripetoken',
            old_name='content',
            new_name='stripe_js_response',
        ),
        migrations.AlterField(
            model_name='stripecharge',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='stripe_charges', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='stripetoken',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='stripe_tokens', to=settings.AUTH_USER_MODEL),
        ),
    ]
