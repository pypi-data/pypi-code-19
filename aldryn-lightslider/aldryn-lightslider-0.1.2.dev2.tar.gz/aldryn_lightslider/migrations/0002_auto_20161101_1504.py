# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('aldryn_lightslider', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='lightsliderplugin',
            name='transition_style',
            field=models.CharField(default=b'', max_length=50, verbose_name='Transition Style', blank=True, choices=[(b'slide', 'Slide'), (b'fade', 'Fade')]),
        ),
        migrations.AlterField(
            model_name='lightsliderplugin',
            name='transition_effect',
            field=models.CharField(default=b'', max_length=50, verbose_name='Transition Effect', blank=True, choices=[(b'linear', 'Linear'), (b'ease', 'Ease'), (b'ease-in', 'Ease in'), (b'ease-out', 'Ease out'), (b'ease-in-out', 'Ease in out')]),
        ),
    ]
