# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fluentcms_button', '0002_buttonitem_align'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='buttonitem',
            name='block',
        ),
    ]
