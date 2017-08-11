# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import time


class Migration(migrations.Migration):

    dependencies = [
        ('otree', '0022_remove_session_mturk_qualification_type_id'),
    ]

    operations = [
        migrations.CreateModel(
            name='ChatMessage',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('channel', models.CharField(max_length=255)),
                ('nickname', models.CharField(max_length=255)),
                ('body', models.TextField()),
                ('timestamp', models.FloatField(default=time.time)),
                ('participant', models.ForeignKey(to='otree.Participant')),
            ],
        ),
        migrations.CreateModel(
            name='NicknameRegistration',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('channel', models.CharField(max_length=255)),
                ('nickname', models.CharField(max_length=255)),
                ('participant', models.ForeignKey(to='otree.Participant')),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='nicknameregistration',
            unique_together=set([('channel', 'participant')]),
        ),
        migrations.AlterIndexTogether(
            name='chatmessage',
            index_together=set([('channel', 'timestamp')]),
        ),
    ]
