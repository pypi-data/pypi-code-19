# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


def create_yourtips_index(apps, schema_editor):
    from molo.core.models import Main
    from molo.yourtips.models import (
        YourTipsIndexPage, YourTipsSectionIndexPage
    )
    main = Main.objects.all().first()

    if main:
        tip_index = YourTipsIndexPage(title='Your Tips', slug='your-tips')
        main.add_child(instance=tip_index)
        tip_index.save_revision().publish()
        tip_section_index = YourTipsSectionIndexPage(
            title='Converted Tips', slug='converted-tips'
        )
        main.add_child(instance=tip_section_index)
        tip_section_index.save_revision().publish()


class Migration(migrations.Migration):

    dependencies = [
        ('yourtips', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_yourtips_index),
    ]
