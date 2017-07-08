# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-05-24 04:56
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('document_indexing', '0010_documentindexinstancenode_indexinstance'),
    ]

    operations = [
        migrations.AlterField(
            model_name='indextemplatenode',
            name='expression',
            field=models.TextField(
                help_text="Enter a template to render. Use Django's default "
                "templating language (https://docs.djangoproject.com/en/1.7/"
                "ref/templates/builtins/)",
                verbose_name='Indexing expression'
            ),
        ),
    ]
