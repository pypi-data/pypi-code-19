# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-06-13 14:04
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('infernoWeb', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create', models.DateTimeField(default=django.utils.timezone.now)),
                ('raw', models.CharField(max_length=500)),
                ('like', models.PositiveSmallIntegerField(default=0)),
                ('emotion', models.CharField(choices=[('neutral', 'neutral'), ('pos', 'pos'), ('neg', 'neg')], default='neutral', max_length=7)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='infernoWeb.User')),
            ],
        ),
        migrations.CreateModel(
            name='Course',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=10)),
                ('ctype', models.CharField(default='', max_length=10)),
                ('dept', models.CharField(default='', max_length=20)),
                ('avatar', models.ImageField(default='', upload_to='')),
                ('teacher', models.CharField(max_length=10)),
                ('school', models.CharField(max_length=10)),
                ('book', models.CharField(max_length=50)),
                ('feedback_amount', models.PositiveIntegerField(default=0)),
                ('feedback_freedom', models.FloatField(default=3)),
                ('feedback_FU', models.FloatField(default=3)),
                ('feedback_easy', models.FloatField(default=3)),
                ('feedback_GPA', models.FloatField(default=3)),
                ('feedback_knowledgeable', models.FloatField(default=3)),
                ('benchmark', models.CharField(default='', max_length=60)),
                ('attendee', models.ManyToManyField(to='infernoWeb.User')),
            ],
        ),
        migrations.CreateModel(
            name='LikesFromUser',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('author', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='infernoWeb.User')),
                ('comment', models.ManyToManyField(to='slothTw.Comment')),
            ],
        ),
        migrations.CreateModel(
            name='PageLog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create', models.DateTimeField(default=django.utils.timezone.now)),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='slothTw.Course')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='infernoWeb.User')),
            ],
        ),
        migrations.AddField(
            model_name='comment',
            name='course',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='slothTw.Course'),
        ),
    ]
