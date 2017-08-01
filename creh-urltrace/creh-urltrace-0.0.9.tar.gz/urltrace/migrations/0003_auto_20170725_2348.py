# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('urltrace', '0002_initial_data'),
    ]

    operations = [
        migrations.AlterField(
            model_name='urltracegroup',
            name='group_name',
            field=models.CharField(unique=True, max_length=200),
            preserve_default=True,
        ),
    ]
