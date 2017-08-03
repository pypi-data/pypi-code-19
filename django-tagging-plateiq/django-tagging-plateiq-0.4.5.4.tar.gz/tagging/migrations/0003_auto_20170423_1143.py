# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tagging', '0002_on_delete'),
    ]

    operations = [
        migrations.AlterField(
            model_name='taggeditem',
            name='object_id',
            field=models.TextField(verbose_name='object id', db_index=True),
        ),
    ]
