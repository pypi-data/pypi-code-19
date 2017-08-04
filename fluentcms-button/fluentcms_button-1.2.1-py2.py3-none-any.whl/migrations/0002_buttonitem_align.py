# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fluentcms_button', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='buttonitem',
            name='align',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='Alignment', choices=[('', 'Inline'), ('left', 'Left'), ('center', 'Center'), ('right', 'Right'), ('block', 'Full Width')]),
        ),
    ]
