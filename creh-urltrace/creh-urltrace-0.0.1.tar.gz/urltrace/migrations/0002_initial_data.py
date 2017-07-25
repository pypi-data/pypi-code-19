# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations

def load_first_data(apps, schema_editor):
    UrlTraceGroup = apps.get_model('urltrace', 'UrlTraceGroup')
    UrlTraceGroup.objects.create(group_name="general",
                                 description="general group of urls")

class Migration(migrations.Migration):

    dependencies = [
        ('urltrace', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(load_first_data),
    ]